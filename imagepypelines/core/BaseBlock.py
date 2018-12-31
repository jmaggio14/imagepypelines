# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018 Jeff Maggio, Nathan Dileas, Ryan Hartzell
from .Printer import get_printer
from .Exceptions import InvalidBlockInputData
from .Exceptions import InvalidProcessStrategy
from .Exceptions import InvalidLabelStrategy
from .Exceptions import DataLabelMismatch
from .Exceptions import BlockRequiresLabels
from .Exceptions import IncompatibleTypes
from .constants import NUMPY_TYPES
import copy
from abc import ABCMeta, abstractmethod

class ArrayType(object):
    """Object to describe the shapes of Arrays for Block inputs or outputs

    Object that contains the shapes and datatypes of an input or output
    for a BaseBlock

    Args:
        *array_shapes(vargs of array shapes): acceptable shapes. Arbitrary
            length axes can be represented by None.
            example: [None,None,3] (for rgb image)
    """
    def __init__(self, *array_shapes):
        if len(array_shapes) > 0:
            # -------------------- error-checking ---------------------
            if not all(isinstance(shape, (tuple, list)) for shape in array_shapes):
                raise TypeError("all array shapes must be tuples or lists")

            # ensure that every element is a positive integer or NoneType
            shapes = list(list(shp) for shp in array_shapes)
            for shp in shapes:
                for i in range( len(shp) ):
                    if isinstance(shp[i],(float,int)):
                        assert shp[i] > 0, "elements of shape must be > 0 or None"
                        shp[i] = int(shp[i])

                    elif not (shp[i] is None):
                        error_msg = "all elements must be positive integers or None"
                        raise ValueError(error_msg)

            # -------------------- create instance variables ---------------------
            self.shapes = tuple(tuple(shp) for shp in shapes)

        else:
            self.shapes = ()

        self.arbitrary = not bool( len(self.shapes) )

    def __str__(self):
        if len(self.shapes) == 0:
            return "ArrayType(<arbitrary shape>)"
        else:
            return "ArrayType({})".format(', '.join(self.shapes))

    def __repr__(self):
        return str(self)
#
    def __eq__(self,other):
        if isinstance(other,ArrayType):
            return hash(self) == hash(other)
        return False
#
    def __hash__(self):
        # NOTE(Jeff Maggio) - possible issue here because tuples aren't sorted
        clean = lambda shp : tuple((-1 if ele is None else ele) for ele in shp)
        sortable = (clean(shp) for shp in self.shapes)
        return hash( tuple(sorted(sortable)) )



class Same(object):
    """class meant to be the output in an IoMap.
    Indicates that the output is the same as the input is returned"""
    pass

class Incompatible(object):
    def __str__(self):
        return "No known outputs due to incompatible Inputs"

class IoMap(tuple):
    """mapping object to determine the output of block
    IoMaps are used to predict the output of a block given a certain type of
    input. Every block contains an IoMap located under block.io_map
    Args:
        io_map(dict,IoMap): dictionary that describes the input outputs of the
            block. Of the form: io_map[input_type] = output_type
    Attributes:
        non_arrays(tuple): mapping of non-array input-outputs for this io_map
        arrays(tuple): mapping of array input-outputs for this io_map
        inputs(tuple): tuple of inputs for this io map
        outputs(tuple): tuple of outputs for this io map
    """
    def __new__(cls, io_map):
        # -------------- ERROR CHECKING -----------------------
        if isinstance(io_map, IoMap):
            return io_map
        elif not isinstance(io_map, dict):
            raise TypeError("IoMap must be instantiated with a dictionary")

        # ---------------- Breaking dictionary up into a mapping --------------
        # {key1:val1,key2:val2} --> ( (key1,val1),(key2,val2) )
        io_map = io_map.items()
        # splitting apart all Array Types with multiple shapes
        # ArrayType(shape1,shape2) --> ArrayType(shape1), ArrayType(shape2)
        # going through inputs first
        reduced_io_map = []
        for i, o in io_map:
            reduced_io_map.extend(cls.reduce(i, o))

        # return the new reduced mapping
        return super(IoMap, cls).__new__(cls, tuple(set(reduced_io_map)))

    def __init__(self, io_map):
        self.non_arrays = tuple((i, o) for i, o in self if (not isinstance(i, ArrayType)))
        self.arrays = tuple((i, o) for i, o in self if isinstance(i, ArrayType))

        self.inputs = tuple(i for i, o in self)
        self.outputs = tuple(o for i, o in self)

    @staticmethod
    def reduce(i, o):
        """reduces ArrayTypes with multiple shapes to multiple single
        shape ArrayTypes
        ArrayType(shape1,shape2) --> ArrayType(shape1), ArrayType(shape2)
        Args:
            i (ArrayType): block input
            o (ArrayType): block output
        Returns:
            reduced(tuple): tuple mapping of reduced types ((i1,o1),(i2,o2)...)
        """
        if not isinstance(i,ArrayType):
            reduced_i = ((i, o), )
        else:
            split = tuple(ArrayType(shp) for shp in i.shapes)
            reduced_i = zip(split, (o,)*len(split))

        reduced = []
        for i, o in reduced_i:
            if not isinstance(o,ArrayType):
                reduced.append((i, o))
            else:
                split = tuple(ArrayType(shp) for shp in o.shapes)
                reduced.extend(zip((i,)*len(split), split))

        return tuple( reduced )

    @staticmethod
    def shape_comparison(input_array, acceptable_array):
        """compares ArrayType shapes and returns a boolean to indicate
        compatability
        Args:
            input_array(tuple): input ArrayType
            acceptable_array(tuple): Acceptable ArrayTypes
        Returns:
            compatible(bool): whether or the input shape is compatible with
                this block
        """
        # if the acceptable array has an arbitrary shape, then it's compatible
        # no matter what
        if acceptable_array.arbitrary:
            return True

        # if they have a different number of axis, they aren't compatible
        if len(input_array.shape) != len(acceptable_array.shape):
            return False

        # compare every element
        compatible_by_axis = []
        for input_i, acceptable_i in zip(input_shape, acceptable_shape):
            # if block element is None, then arbitrary length for this axis is accepted
            # so no more comparisons are needed for this element
            if (acceptable_i == None) or (input_i == acceptable_i):
                compatible_by_axis.append(True)
            else:
                compatible_by_axis.append(False)

        return all(compatible_by_axis)

    def output(self, input_types):
        """gets the given output(s) of this IoMap given a input type or types
        Args:
            input_types(tuple,set): tuple or set of input types
        Returns:
            outputs(set): tuple of output types this block produces given the
                input_types
        """
        outputs = set()

        for input_type in input_types:
            # Quick Check for direct matches
            if input_type in self.inputs:
                indices = [idx for idx,it in enumerate(self.inputs) if (it==input_type)]
                for idx in indices:
                    out = self.outputs[idx]
                    if isinstance(out,Same):
                        outputs.add( self.inputs[idx] )
                    else:
                        outputs.add( out )

            elif isinstance(input_type, ArrayType):
                for arr_in,arr_out in self.arrays:
                    if self.shape_comparison(input_type,arr_in):
                        if isinstance(out,Same):
                            outputs.add(arr_in)
                        else:
                            outputs.add(arr_out)


            else:
                raise IncompatibleTypes("invalid input type, must be ({})"\
                     + "not {}".format(self.inputs,input_type))


            return outputs

















class BaseBlock(object):
    """BaseBlock object which is the root class for SimpleBlock and BatchBlock
    subclasses

    This is the building block (pun intended) for the entire imagepypelines
    pipelining system. All blocks, both SimpleBlocks and BatchBlocks, will
    inherit from this object. Which contains base functionality to setup a
    block's printers, unique name, standard input/output_shapes and special
    functions for pipeline objects to call

    Args:
        io_map(IoMap,dict): dictionary of input-output mappings for this
            Block
        name(str): name for this block, it will be automatically created/modified
            to make sure it is unique
        notes(str): a short description of this block
        requires_training(bool): whether or not this block will require
            training
        requires_labels(bool): whether or not this block will require
            labels during training

    Attributes:
        io_map(IoMap): object that maps inputs to this block to outputs
            subclass of tuple where I/O is stored as:
            ( (input1,output1),(input2,output2)... )
        name(str): unique name for this block
        notes(str): a short description of this block
        requires_training(bool): whether or not this block will require
            training
        trained(bool): whether or not this block has been trained, True
            by default if requires_training = False
        printer(ip.Printer): printer object for this block,
            registered to 'name'

    """
    __metaclass__ = ABCMeta
    EXTANT = {}
    def __init__(self,
                 io_map,
                 name=None,
                 notes=None,
                 requires_training=False,
                 requires_labels=False,
                 ):
        # ----------- building a unique name for this block ------------
        if name is None:
            name = self.__class__.__name__

        # JM: keeping track of names in base class variable
        if name in self.EXTANT:
            self.EXTANT[name] += 1
        else:
            self.EXTANT[name] = 1
        name = name + ':{}'.format( self.EXTANT[name] )


        # checking if notes were provided for this block
        if notes is None:
            notes = "No Description provided by the author"
        if not isinstance(notes,str):
            raise TypeError("notes must be a string description or None")

        # ------ setting up instance variables
        self.io_map = IoMap(io_map)
        self.name = name
        self.notes = notes
        self.requires_training = requires_training
        self.requires_labels = requires_labels

        self.trained = False
        if not self.requires_training:
            self.trained = True

        self.printer = get_printer(self.name)

        super(BaseBlock,self).__init__()

    def rename(self,name):
        """Renames this block to the given name

        Args:
            name(str): the new name for your Block

        Returns:
            ip.Block : object reference to this block (self)

        Note:
            unlike naming your block using the `name` parameter in
            instantiation, imagepypelines will not guarantee that this name
            will be unique. It is considered the user's responsibility to
            determine that this will not cause problems in your pipeline.
        """
        assert isinstance(name,str),"name must be a string"
        self.name = name
        self.printer = get_printer(self.name)
        return self

    def train(self, data, labels=None):
        """(optional or required overload)trains the block. overloading
        is required if the 'requires_training' parameter is set to True

        users are expected to save pertinent variables as instance
        variables

        Args:
            data(list): list of datums to train on
            labels(list,None): corresponding label for each datum,
                None by default (for unsupervised systems)

        Returns:
            None
        """
        if self.requires_training:
            msg = "{}.train must be overloaded if the " \
                        + "'requires_training' is set to True".format(self.name)
            self.printer.critical(msg)
            raise NotImplementedError(msg)

    def before_process(self, data, labels=None):
        """(optional overload)function that runs before processing for
        optional functionality. this function takes in the full data list and
        label list. does nothing unless overloaded

        Args:
            data(list): list of datums to process
            labels(list,None): corresponding label for each datum,
                None by default (for unsupervised systems)
        """
        pass

    def after_process(self):
        """
        (optional overload)function that runs after processing for
        optional functionality. intended for optional use as a cleanup
        function

        Args:
            None
        """
        pass

    def _pipeline_train(self, data, labels=None):
        """function pipeline calls to train this block, modifies
        self.trained status

        Args:
            data(list): list of datums to train on
            labels(list,None): corresponding label for each datum,
                None by default (for unsupervised systems)

        Returns:
            None

        Raises:
            BlockRequiresLabels: if this block requires labels and None
                was passed in
        """
        if self.requires_labels and (labels is None):
            msg = "{} requires labels for training but none were passed in"\
                .format(self)
            raise BlockRequiresLabels(msg)

        if isinstance(labels,list):
            # if labels are passed in, we must have an equal number
            # of datums and labels
            if len(data) != len(labels):
                raise DataLabelMismatch(data, labels)

        self.train(data, labels)
        self.trained = True

    def _pipeline_process(self, data, labels=None):
        """function pipeline calls to process data using this block
        works with BatchBlocks and SimpleBlocks

        Args:
            data(list): list of datums to process
            labels(list,None): corresponding label for each datum,
                None by default (for unsupervised systems)

        Returns:
            processed(list): list of processed datums
            labels(list): list of corresponding labels for processed

        Raises:
            InvalidBlockInputData: if data is not a list or tuple
            InvalidProcessingStrategy: if processed output is not a list
            InvalidLabelStrategy: if labels output is not a list
            DataLabelMismatch: if there is mismatch in the number of labels
                and processed datums

        """
        # ---------------- INPUT ERROR CHECKING ------------------------
        if not isinstance(data, list):
            error_msg = "input data into a block must be a list"
            self.printer.error(error)
            raise InvalidBlockInputData(self)

        if labels is None:
            labels = [None] * len(data)

        if isinstance(labels,list):
            if len(data) != len(labels):
                raise DataLabelMismatch(processed, labels)

        # ----------- running block functions -----------------------
        # running prep function
        self.before_process(data, labels)

        # processing data and labels
        processed = self.process_strategy(data)
        labels = self.label_strategy(labels)

        # running post-process / cleanup function
        self.after_process()


        # --------------- OUTPUT ERROR CHECKING ------------------------
        # error checking for output types
        if not isinstance(processed, list):
            raise InvalidProcessStrategy(self)

        if not isinstance(labels, list):
            raise InvalidLabelStrategy(self)

        # making sure that we always have the same number of labels and datums
        if len(processed) != len(labels):
            raise DataLabelMismatch(processed, labels)

        return processed, labels

    @abstractmethod
    def process_strategy(self, data):
        """overarching processing management function for this block

        Args:
            data(list): list of datums to process

        Returns:
            list: processed datums
        """
        raise NotImplementedError("'process_strategy' must be overloaded in all children")

    @abstractmethod
    def label_strategy(self, labels):
        """overarching label management function for this block

        Args:
            labels(list,None): corresponding label for each datum,
                None by default (for unsupervised systems)

        Returns:
            labels (list): labels for datums (Nones for unsupervised systems)
        """
        raise NotImplementedError("'label_strategy' must be overloaded in all children")

    def __str__(self):
        return self.name

    def __repr__(self):
        return (str(self) + '\n' + self.notes)

    def prep_for_serialization(self):
        pass

    def restore_from_serialization(self):
        pass


# END
