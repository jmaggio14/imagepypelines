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

from uuid import uuid4
from abc import ABCMeta, abstractmethod
import inspect

########################################################################


class Block(object):
    __metaclass__ = ABCMeta
    def __init__(self, name=None, batch_size="all"):
        assert batch_size in ["all","singles"] or isinstance(batch_size,int)

        # setup absolutely unique id for this block
        self.uuid = uuid4().hex

        # ------ setting up instance variables
        if name is None:
            name = self.__class__.__name__
        self.name = name
        self.batch_size = batch_size

        # this will be defined in _pipeline_pair
        self.logger = get_logger( self.id )

        # setup initial tags
        self.tags = set()

        # whether or not the input names have been defined for this block
        self._arg_spec = None

        super(Block,self).__init__() # for metaclass?

    @staticmethod
    def process(self,*data):
        pass

    def _pipeline_process(self, *data, logger):
        self._pair_logger(logger)
        # NOTE: add type checking here

        # check data partity (same n_items for every data)
        # this still works even if len(data) is 0
        if not all(data[0].n_batches_with(self.batch_size) == d.n_batches_with(self.batch_size) for d in data):
            msg = "Invalid data lengths! all data must have the same"\
                    + "number of items. {}"
            # this adds a list ("input_name.n_items"=)
            msg.format(",".join("{}.n_items={}".format(d.n_items) for i,d in zip(self.inputs,data)))
            self.logger.error(msg)
            raise RuntimeError(msg)

        # root blocks don't need input data, and won't have any data
        # passed in to batch. We only call process once for these
        if len(self.inputs) == 0:
            # Note: I think this will lead to errors for block with
            # more than one output, but no inputs - JM
            ret = tuple(self.process() for i in range(1))
        else:
            # otherwise we prepare to batch the data and run it through process
            # prepare the batch generators
            batches = [d.batch_as(self.batch_size) for d in data]
            # feed the data into the process function in batches
            outputs = (self.process(*datums) for datums in zip(*batches))
            ret = tuple( zip(*outputs) )

        self._unpair_logger()
        return ret

    def _pair_logger(self, pipeline_logger):
        self.logger = pipeline_logger.getChild(self.id)

    def _unpair_logger(self):
        self.logger = get_logger(self.id)

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)

    def get_default_node_attrs(self):
        attrs = { 'name':self.name,
        'type':type(self),
        'color': 'orange',
        'shape':'square',
        }
        return attrs


    @property
    def inputs(self):
        if self._arg_spec is None:
            self._arg_spec = inspect.getfullargspec(self.process)
        # save the argspec in an instance variable if it hasn't been computed
        if (self._arg_spec.args is None):
            return []
        else:
            return self._arg_spec.args[1:] # ignoring 'self'


    @property
    def id(self):
        return "{}#{}".format(self.name, self.uuid[-UUID_ORDER:])

# NOTE: add 'summarize' function -- spits out block metadata






# # END
