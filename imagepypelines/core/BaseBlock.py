# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018-2019 Jeff Maggio, Nathan Dileas, Ryan Hartzell
from ..Logger import get_logger
from ..Logger import ImagepypelinesLogger
from .Exceptions import InvalidBlockInputData
from .Exceptions import InvalidProcessStrategy
from .Exceptions import InvalidLabelStrategy
from .Exceptions import DataLabelMismatch
from .Exceptions import BlockRequiresLabels
from .Exceptions import IncompatibleTypes
from .constants import NUMPY_TYPES

import copy
import time
from uuid import uuid4
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
                for i in range(len(shp)):
                    if isinstance(shp[i], (float, int)):
                        assert shp[i] > 0, "elements of shape must be > 0 or None"
                        shp[i] = int(shp[i])

                    elif not (shp[i] is None):
                        error_msg = "all elements must be positive integers or None"
                        raise ValueError(error_msg)

            # -------------------- create instance variables ---------------------
            self.shapes = tuple(tuple(shp) for shp in shapes)

        else:
            self.shapes = ()

        self.arbitrary = not bool(len(self.shapes))

    def __str__(self):
        if len(self.shapes) == 0:
            return "ArrayType(<arbitrary shape>)"
        else:
            return "ArrayType({})".format(', '.join(str(s) for s in self.shapes))

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if isinstance(other, ArrayType):
            return hash(self) == hash(other)
        return False

    def __hash__(self):
        # NOTE(Jeff Maggio) - possible issue here because tuples aren't sorted
        clean = lambda shp: tuple((-1 if ele is None else ele) for ele in shp)
        sortable = (clean(shp) for shp in self.shapes)
        return hash(tuple(sorted(sortable)))


class Same(object):
    """class meant to be the output in an IoMap.
    Indicates that the output is the same as the input is returned"""
    pass


class Incompatible(object):
    def __str__(self):
        return "No known outputs due to incompatible Inputs"

    def __repr__(self):
        return str(self)


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
        elif isinstance(io_map, dict):
            io_map = io_map.items()
        elif not isinstance(io_map, tuple):
            raise TypeError(
                "IoMap must be instantiated with a dictionary, tuple, or other IoMap, not %s"
                % type(io_map))

        # ---------------- Breaking dictionary up into a mapping --------------
        # {key1:val1,key2:val2} --> ( (key1,val1),(key2,val2) )
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
            tuple: mapping of reduced types ((i1,o1),(i2,o2)...)
        """
        if not isinstance(i, ArrayType):
            reduced_i = ((i, o), )
        else:
            if i.arbitrary:
                split = (ArrayType(),)
            else:
                split = tuple(ArrayType(shp) for shp in i.shapes)
            reduced_i = zip(split, (o,)*len(split))

        reduced = []
        for i, o in reduced_i:
            if not isinstance(o, ArrayType):
                reduced.append((i, o))
            else:
                if o.arbitrary:
                    split = (ArrayType(),)
                else:
                    split = tuple(ArrayType(shp) for shp in o.shapes)
                reduced.extend(zip((i,)*len(split), split))

        return tuple(reduced)

    @staticmethod
    def shape_comparison(input_array, acceptable_array):
        """compares ArrayType shapes and returns a boolean to indicate
        compatability
        Args:
            input_array(tuple): input ArrayType
            acceptable_array(tuple): acceptable ArrayTypes
        Returns:
            compatible(bool): whether or the input shape is compatible with
                this block
        """
        # if the acceptable array has an arbitrary shape, then it's compatible
        # no matter what
        if acceptable_array.arbitrary:
            return True

        input_shape = input_array.shapes[0]
        acceptable_shape = acceptable_array.shapes[0]

        # if they have a different number of axis, they aren't compatible
        if len(input_shape) != len(acceptable_shape):
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
                indices = [idx for idx, it in enumerate(self.inputs) if (it == input_type)]
                for idx in indices:
                    out = self.outputs[idx]
                    if isinstance(out, Same):
                        outputs.add(self.inputs[idx])
                    else:
                        outputs.add(out)

            elif isinstance(input_type, ArrayType):
                for arr_in, arr_out in self.arrays:
                    if self.shape_comparison(input_type, arr_in):
                        if isinstance(arr_out, Same):
                            outputs.add(arr_in)
                        else:
                            outputs.add(arr_out)

            else:
                raise IncompatibleTypes("invalid input type, must be"
                     + "({}) not {}".format(self.inputs, input_type))

            return tuple(outputs)

    def __str__(self):
        return repr(self)

    def __repr__(self):
        # create a 'readable' io map that simply replaces outputs defined as 'Same'
        # with it's corresponding input
        # (ArrayType((512,512)),Same)-->(ArrayType((512,512)),ArrayType((512,512)))
        io = []
        for i, o in self:
            if isinstance(o, Same) and isinstance(i, ArrayType):
                o = str(i) + " [same shape as input]"
            io.append((i, o))

        io_map_str = "\n".join("{} --> {}".format(i, o) for i, o in io)
        return io_map_str

    # def __reduce__(self):
    #     """make io maps copyable and serializable"""
    #     constructor = IoMap
    #     args = tuple( (i,o) for i,o in self )
    #     return constructor, args


def describe_block(block, notes):
    if notes is None:
        notes = "<no description provided by the author>"

    io_map_str = repr(block.io_map)
    description = \
"""{name}

{notes}

io mapping:
{io_map}""".format(name=block.name, notes=notes, io_map=io_map_str)

    return description


class BaseBlock(object):
    """BaseBlock object which is the root class for SimpleBlock and BatchBlock
    subclasses

    This is the building block (pun intended) for the entire imagepypelines
    pipelining system. All blocks, both SimpleBlocks and BatchBlocks, will
    inherit from this object. Which contains base functionality to setup a
    block's loggers, unique name, standard input/output_shapes and special
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
        io_map(IoMap): object that maps inputs to this block to it's outputs.
            subclass of tuple where I/O is stored as:
            ( (input1,output1),(input2,output2)... )
        name(str): unique name for this block
        notes(str): a short description of this block, what operations it
            performs, etc. This will be included in the blocks 'description'
        requires_training(bool): whether or not this block will require
            training
        trained(bool): whether or not this block has been trained, True
            by default if requires_training = False
        logger(ip.ImagepypelinesLogger): logger for this block,
            registered to 'name'
        description(str): a readable description of this block that includes
            user defined notes and a summary of inputs and outputs
    """
    __metaclass__ = ABCMeta
    def __init__(self,
                 io_map,
                 name=None,
                 notes=None,
                 requires_training=False,
                 requires_labels=False,
                 ):
         # this uuid will not change with copying or serialization
         # as such it can be used to id which blocks are copies or unpickled
         # versions of the original - it's metaphorical siblings
        self.sibling_id = uuid4().hex
        # setup absolutely unique id for this block
        # this will change even if the block is copied or pickled
        self.uuid = uuid4().hex
        # ----------- building a unique name for this block ------------
        # logger_name is set up as follows
        # <readable_name>-<sibling_id>-<uuid>
        if name is None:
            name = self.__class__.__name__
        logger_name = self.__get_logger_name(name,
                                                self.sibling_id,
                                                self.uuid)

        # ------ setting up instance variables
        self.io_map = IoMap(io_map)
        self.name = name
        self.logger_name = logger_name
        self.requires_training = requires_training
        self.requires_labels = requires_labels
        self.trained = False if self.requires_training else True

        # this will be defined in _pipeline_pair
        self.logger = None
        self.pipeline_uuid = None
        self.pipeline_name = None

        # create a block description
        self.description = describe_block(self,notes)

        # setup initial metadata dictionary
        self._metadata = {'processing_time':0.0,
                            'num_in':int(0),
                            'num_out':int(0),
                            'total_in':int(0),
                            'total_out':int(0),
                            'training_time':None,
                            }

        # setup initial tags
        self.tags = set()


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
        self.logger_name = self.__get_logger_name(self.name,
                                                    self.sibling_id,
                                                    self.uuid)
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
            self.logger.critical(msg)
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
        start = time.time()
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

        # update metadata
        self._metadata['training_time'] = round(time.time() - start,3)

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
            InvalidBlockInputData: if data is not a list
            InvalidProcessingStrategy: if processed output is not a list
            InvalidLabelStrategy: if labels output is not a list
            DataLabelMismatch: if there is mismatch in the number of labels
                and processed datums

        """
        start = time.time()
        # ---------------- INPUT ERROR CHECKING ------------------------
        if not isinstance(data, list):
            raise InvalidBlockInputData(
                "input data into a block must be a list")

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

        # update the metadata
        self._metadata['num_in'] = len(data)
        self._metadata['num_out'] = len(processed)
        self._metadata['processing_time'] = round(time.time() - start,5)
        self._metadata['total_in'] += len(data)
        self._metadata['total_out'] += len(processed)
        return processed, labels


    def _pipeline_pair(self, pipeline):
        """pairs this block for use with the pipeline passed in

        Args:
            pipeline (ip.Pipeline): the pipeline to pair with this block

        Returns:
            None
        """
        self.logger = pipeline.logger.getChild( self.logger_name )
        self.pipeline_name = pipeline.name
        self.pipeline_uuid = pipeline.uuid

    @abstractmethod
    def process_strategy(self, data):
        """overarching processing management function for this block

        Args:
            data(list): list of datums to process

        Returns:
            list: processed datums
        """
        raise NotImplementedError(
            "'process_strategy' must be overloaded in all children")

    @abstractmethod
    def label_strategy(self, labels):
        """overarching label management function for this block

        Args:
            labels(list,None): corresponding label for each datum,
                None by default (for unsupervised systems)

        Returns:
            labels (list): labels for datums (Nones for unsupervised systems)
        """
        raise NotImplementedError(
            "'label_strategy' must be overloaded in all children")

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.description

    def __getstate__(self):
        """pickle state retrieval function, its most important use is to
        delete the copied uuid to prevent potential issues from improper
        restoration

        Note:
            If you overload this function, it's imperative that you call this
            function via _super().__getstate__(state)_, or otherwise return
            a state dictionary without a uuid
        """
        state = self.__dict__.copy()
        del state['uuid']
        return state

    def __setstate__(self, state):
        """pickle restoration function, its most important use is to generate
        a new uuid for the copied or deserialized object

        Note:
            If you overload this function, it's imperative that you call this
            function via _super().__setstate__(state)_, or otherwise create a
            new unique uuid for the restored Block _self.uuid = uuid4().hex_
        """
        self.__dict__.update(state)
        # create a new uuid for this instance, since it's technically a
        # different object
        self.uuid = uuid4().hex
        # update the name to correspond with the new uuid
        logger_name = self.__get_logger_name(self.name,
                                                self.sibling_id,
                                                self.uuid)



    @staticmethod
    def __get_logger_name(basename, sibling_id, uuid):
        """generates a unique logger name that contains both a sibling id
        (a random string that will be persistent across all copies and unpickled
        versions of this object) and a uuid (which is unique to this exact
        object instance)
        (only the last six chars of each hash is used, so it's technically possible
        for this name to not be unique) - if you need a truly unique ID, then
        use obj.uuid
        """
        return "{basename} #{sibling_id}-{uuid}".format(basename=basename,
                                                sibling_id=sibling_id[-5:],
                                                uuid=uuid[-5:])



# END
