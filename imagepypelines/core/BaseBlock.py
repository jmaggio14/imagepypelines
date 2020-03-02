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
from .constants import NUMPY_TYPES, UUID_ORDER

import copy
import time
from uuid import uuid4
from abc import ABCMeta, abstractmethod
import inspect

import networkx as nx

class BaseBlock(object):
    __metaclass__ = ABCMeta
    def __init__(self,name=None):
        # setup absolutely unique id for this block
        # this will change even if the block is copied or pickled
        self.uuid = uuid4().hex

        # ------ setting up instance variables
        if name is None:
            name = self.__class__.__name__
        self.name = name

        # this will be defined in _pipeline_pair
        self.logger = get_logger( self.id )

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

    @abstractmethod
    def inputs(self):
        pass

    def get_default_node_attrs(self):
        attrs = { 'name':self.name,
                    'type':type(self),
                    'color': 'orange',
                    'shape':'square',
                    }
        return attrs

    @property
    def id(self):
        return "{}.{}".format(self.name, self.uuid[-UUID_ORDER:])

# NOTE: add 'summarize' function -- spits out block metadata






# # END
