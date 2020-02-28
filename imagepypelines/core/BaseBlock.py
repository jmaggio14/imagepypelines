# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018-2020 Jeff Maggio, Nathan Dileas, Ryan Hartzell
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
import inspect

import networkx as nx

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
        n_inputs(int): number of data inputs to block (len of data input INCLUDING TRAIN DATA ***TENTATIVE CHANGE USING **kwargs DICT IN PROCESS AND TRAIN AS A INSTANCE VARIABLE!!!: RYAN)
        n_outputs(int): number of data outputs to block (len of data output)
        inputs(dict): key names of input data corresponding to each index in data
        outputs(dict): key names of output data corresponding to each index in return tuple
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
    def __init__(self,name=None):
        # setup absolutely unique id for this block
        # this will change even if the block is copied or pickled
        self.uuid = name + '-' + uuid4().hex if name is not None else self.__class__.__name__ + '-' + uuid4().hex
        # ----------- building a unique name for this block ------------
        # logger_name is set up as follows
        # <readable_name>-<sibling_id>-<uuid>
        if name is None:
            name = self.__class__.__name__
        logger_name = self.__get_logger_name(name,self.uuid)

        # ------ setting up instance variables
        self.name = name
        self.logger_name = logger_name

        # this will be defined in _pipeline_pair
        self.logger = None

        # setup initial tags
        self.tags = set()

        # whether or not the input names have been defined for this block
        self._arg_spec = None

        super(BaseBlock,self).__init__()

    def _pipeline_process(self, *data):
        return self.process_strategy(*data)

    @abstractmethod
    def process_strategy(self, *data):
        """overarching processing management function for this block

        Args:
            data(list): list of datums to process

        Returns:
            list: processed datums
        """
        raise NotImplementedError(
            "'process_strategy' must be overloaded in all children")

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)

    @staticmethod
    def __get_logger_name(basename, uuid):
        """generates a unique logger name that contains both a sibling id
        (a random string that will be persistent across all copies and unpickled
        versions of this object) and a uuid (which is unique to this exact
        object instance)
        (only the last six chars of each hash is used, so it's technically possible
        for this name to not be unique) - if you need a truly unique ID, then
        use obj.uuid
        """
        return "{0}#{1}".format(basename,uuid[-6:])

    @abstractmethod
    def inputs(self):
        pass

    def get_default_node_attrs(self):
        attrs = { 'name':self.name,
                    'type':type(self),
                    }
        return attrs

# NOTE: add 'summarize' function -- spits out block metadata






# # END
