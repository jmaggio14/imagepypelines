# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018-2020 Jeff Maggio, Nathan Dileas, Ryan Hartzell
from ..Logger import get_logger
from ..Logger import ImagepypelinesLogger
from .constants import NUMPY_TYPES, UUID_ORDER
from .Exceptions import BlockError

from uuid import uuid4
from abc import ABCMeta, abstractmethod
import inspect


class Block(metaclass=ABCMeta):
    """a contained algorithmic element used to construct pipelines. This class
    is defined to be inherited from, or used in the form of one of its child
    classes.

    Note:
        you must overload Block.process() if you intend to use this class

    Attributes:
        uuid(str): hex uuid for this pipeline
        name(str): user specified name for this pipeline, used to generate
            the unique id. defaults to the name of your subclass
        batch_size(str, int): the size of the batch fed into your process
            function. Will be an integer, "all", or "singles"
        logger(:obj:`ImagepypelinesLogger`): Logger object for this block. When
            run in a pipeline this logger is temporaily replaced with a child of
            the Pipeline's logger
        tags(:obj:`set`): tags to describe this block. unused as of March 2020
        _arg_spec(:obj:`namedtuple`,None): a named tuple describing the
            arguments for this block's process function. Only defined if the
            property `block.args` is accessed.
    """
    def __init__(self, name=None, batch_size="all"):
        """instantiates the block

        Args:
            name(str,None): the name of this block - how it will show up in the
                graph.
            batch_size(str, int): the size of the batch fed into your process
                function. Must be an integer, "all", or "singles"
        """
        assert (batch_size in ["all","singles"] or isinstance(batch_size,int))

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

        # FullArgSpec for this block, defined in self.args
        self._arg_spec = None

        super(Block,self).__init__() # for metaclass?


    ############################################################################
    #                           overloadable
    ############################################################################
    @abstractmethod
    def process(self, *data_batches):
        pass

    ############################################################################
    def check_setup(self, task_args):
        """briefly checks setup with the provided task inputs.

        This function can be overloaded to add additional functionality if
        desired. By default it simply checks if too many or too few arguments
        were provided.

        Args:
            task_args(:obj:`tuple` of :obj:`str`): Arguments for this task

        Note:
            Be very careful making task-specific modifications to the block
            setup in this function. It's called once for every task this block
            is in. Changes made for one task may not apply to another task.
        """
        # too few args
        if len(task_args) < self.n_args:
            msg = "Not enough arguments provided"
            self.logger.error(msg)
            raise BlockError(msg)
        # too many args
        elif len(task_args) > self.n_args:
            msg = "Too many arguments provided"
            self.logger.error(msg)
            raise BlockError(msg)

    ############################################################################
    #                           primary frontend
    ############################################################################
    def rename(self, name):
        """renames the block to the given name. The id is reset in this process"""
        if not isinstance(name,str):
            raise BlockError("name must be string")

        self.logger.warning("being renamed from '%s' to '%s'" % self.name, name)
        old_name = self.name
        self.name = name
        # reset the logger
        self._unpair_logger()
        # log the new name
        self.logger.warning("renamed from '%s' to '%s'" % old_name, self.name)


    ############################################################################
    #                 called by internally or by Pipeline
    ############################################################################
    def _pipeline_process(self, *data, logger):
        """batches and processes data through the block's process function. This
        function is called by Pipeline, and not intended to be called by the
        user.

        Args:
            *data: Variable length list of data
            logger(:obj:`ImagepypelinesLogger`): parent pipeline logger, which
                will be used to create a new child block logger

        Returns:
            (tuple): variable length tuple containing processed data
        """
        self._pair_logger(logger)
        # NOTE: add type checking here

        # check data partity (same n_items for every data)
        # this still works even if len(data) is 0
        if not all(data[0].n_items == d.n_items for d in data):
            msg = "Invalid data lengths! all data must have the same"\
                    + "number of items. {}"
            # this adds a list ("input_name.n_items"=)
            msg.format(",".join("{}.n_items={}".format(d.n_items) for i,d in zip(self.inputs,data)))
            self.logger.error(msg)
            raise RuntimeError(msg)

        # root blocks don't need input data, and won't have any data
        # passed in to batch. We only call process once for these
        if self.n_args == 0:
            # Note: I think this will lead to errors for block with
            # more than one output, but no inputs - JM
            ret = tuple(self.process() for i in range(1))
        else:
            # Note: everything is a generator until the end of this statement
            # otherwise we prepare to batch the data and run it through process
            # prepare the batch generators
            batches = (d.batch_as(self.batch_size) for d in data)
            # feed the data into the process function in batches
            # self.process(input_batch1, input_batch2, ...)
            outputs = (self._make_tuple( self.process(*datums) ) for datums in zip(*batches))
            # outputs = (out1batch1,out2batch1), (out1batch2,out2batch2)
            ret = tuple( zip(*outputs) )

        self._unpair_logger()
        return ret

    ############################################################################
    def get_default_node_attrs(self):
        attrs = { 'name':self.name,
        'type':type(self),
        'color': 'orange',
        'shape':'square',
        }
        return attrs

    ############################################################################
    def _pair_logger(self, pipeline_logger):
        """creates or fetches a new child logger of the pipeline for this block"""
        self.logger = pipeline_logger.getChild(self.id)

    ############################################################################
    def _unpair_logger(self):
        """restores the original block logger"""
        self.logger = get_logger(self.id)

    ############################################################################
    @staticmethod
    def _make_tuple(out):
        """if the output isn't a tuple, put it in one"""
        if isinstance(out, tuple):
            return out
        return (out,)

    ############################################################################
    # def _check_batch(self,d,datatype):


    ############################################################################
    #                            special
    ############################################################################
    def __str__(self):
        return self.name

    ############################################################################
    def __repr__(self):
        return self.id

    ############################################################################
    #                           properties
    ############################################################################
    @property
    def args(self):
        """:obj:`list` of :obj:`str`: arguments in the order they are expected"""
        if self._arg_spec is None:
            self._arg_spec = inspect.getfullargspec(self.process)
        # save the argspec in an instance variable if it hasn't been computed
        if (self._arg_spec.args is None):
            return []
        else:
            # ignoring 'self'
            return self._arg_spec.args[1:]

    ############################################################################
    @property
    def n_args(self):
        """int: number of arguments for the process function"""
        return len(self.args)

    ############################################################################
    @property
    def id(self):
        """str: an unique id for this pipeline

        This id is a combination of the pipeline's non-unique name and
        part of it's uuid (last 6 characters by default).
        The entropy of this id can be increased by increasing ImagePypelines
        UUID_ORDER variable
        """
        return "{}#{}".format(self.name, self.uuid[-UUID_ORDER:])

# NOTE: add 'summarize' function -- spits out block metadata






# # END
