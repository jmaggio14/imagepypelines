# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018-2019 Jeff Maggio, Nathan Dileas, Ryan Hartzell
from .Printer import get_printer
from .Exceptions import InvalidBlockInputData
from .Exceptions import InvalidProcessStrategy
from .Exceptions import InvalidLabelStrategy
from .Exceptions import DataLabelMismatch
from .Exceptions import BlockRequiresLabels
from .Exceptions import IncompatibleTypes
from .constants import NUMPY_TYPES
import copy
import time
import uuid
from abc import ABCMeta, abstractmethod
from .blockio import IoMap

def describe_block(block,notes):
    if notes is None:
        notes = "<no description provided by the author>"

    io_map_str = repr(block.io_map)
    description = \
"""{name}

{notes}

io mapping:
{io_map}""".format(name=block.name,notes=notes,io_map=io_map_str)

    return description

class BaseBlock(object):
    """BaseBlock object which is the root class for SimpleBlock and BatchBlock
    subclasses

    This is the building block (pun intended) for the entire imagepypelines
    pipelining system. All blocks, both SimpleBlocks and BatchBlocks, will
    inherit from this object. Which contains base functionality to setup a
    block's printers, unique name, standard input/output_shapes and special
    functions for pipeline objects to call

    Args:
        io_kernel(list): list of lists containing the io_mapping for this block
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
        notes(str): a short description of this block, what operations it
            performs, etc. This will be included in the blocks 'description'
            variance
        requires_training(bool): whether or not this block will require
            training
        trained(bool): whether or not this block has been trained, True
            by default if requires_training = False
        printer(ip.Printer): printer object for this block,
            registered to 'name'
        description(str): a readable description of this block that includes
            user defined notes and a summary of inputs and outputs
    """
    __metaclass__ = ABCMeta
    EXTANT = {}
    def __init__(self,
                 io_kernel,
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

        # ------ setting up instance variables
        self.io_map = IoMap(io_kernel)
        self.name = name
        self.requires_training = requires_training
        self.requires_labels = requires_labels

        self.trained = False if self.requires_training else True

        self.printer = get_printer(self.name)

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

        # setup absolutely unique 8 char hash id for this block
        self.uuid = uuid.uuid4().hex[:8]

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

    def prep_for_serialization(self):
        pass

    def restore_from_serialization(self):
        pass


# END
