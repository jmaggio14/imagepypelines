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
from .arg_checking import DEFAULT_SHAPE_FUNCS

from uuid import uuid4
from abc import ABCMeta, abstractmethod
import inspect
import copy

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
            function. Will be an integer, "all", or "each"
        logger(:obj:`ImagepypelinesLogger`): Logger object for this block. When
            run in a pipeline this logger is temporaily replaced with a child of
            the Pipeline's logger
        tags(:obj:`set`): tags to describe this block. unused as of March 2020
        _arg_spec(:obj:`namedtuple`,None): a named tuple describing the
            arguments for this block's process function. Only defined if the
            property `block.args` is accessed.
        skip_enforcement(bool): whether or not to enforce type and shape checking
        types(:obj:`dict`): Dictionary of input types. If arg doesn't exist
            as a key, or if the value is None, then no checking is done
        shapes(:obj:`dict`): Dictionary of input shapes. If arg doesn't exist
            as a key, or if the value is None, then no checking is done
        shape_fns(:obj:`dict`): Dictionary of shape functions to retrieve. If
            type(arg_datum) doesn't exist as a key, or if the value is None,
            then no checking is done.
    """
    def __init__(self, name=None, batch_size="all", types=None, shapes=None):
        """instantiates the block

        Args:
            name(str,None): the name of this block - how it will show up in the
                graph.
            batch_size(str, int): the size of the batch fed into your process
                function. Must be an integer, "all", or "each"
            types(:obj:`dict`,None): Dictionary of input types. If arg doesn't
                exist as a key, or if the value is None, then no checking is
                done. If not provided, then will default to args as keys, None
                as values.
            shapes(:obj:`dict`,None): Dictionary of input shapes. If arg doesn't
                exist as a key, or if the value is None, then no checking is
                done. If not provided, then will default to args as keys, None
                as values.
        """
        assert (batch_size in ["all","each"] or isinstance(batch_size,int))

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

        # TYPE AND SHAPE CHECKING VARS
        # ----------------------------------------------------------------------
        self.skip_enforcement = False

        # types
        if types is None:
            self.types = {arg : None for arg in self.args}
        else:
            if not isinstance(types,dict):
                raise TypeError("'types' must be a dictionary or None")
            self.types = types

        # shapes
        if shapes is None:
            self.shapes = {arg : None for arg in self.args}
        else:
            if not isinstance(shapes,dict):
                raise TypeError("'shapes' must be a dictionary or None")
            self.shapes = shapes

        # shape_fns
        if shape_fns is None:
            self.shape_fns = DEFAULT_SHAPE_FUNCS.copy()
        else:
            if not isinstance(shape_fns,dict):
                raise TypeError("'shape_fns' must be a dictionary or None")
            self.shape_fns = shape_fns

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
    def copy(self):
        """fetches a shallow copy of this block with the UUID updated"""
        # NOTE: make sure this results in the same behavior as unpickling
        # the uuid must be updated
        copied = copy.copy(self)
        copied.uuid = uuid4().hex
        return copied

    ############################################################################
    def deepcopy(self):
        """fetches a deep copy of this block with the UUID updated"""
        # NOTE: make sure this results in the same behavior as unpickling
        # the uuid must be updated
        deepcopied = copy.deepcopy(self)
        deepcopied.uuid = uuid4().hex
        return deepcopied

    ############################################################################
    def enforce(self, arg, types=None, shapes=None):
        """sets the block up to make sure the given arg is the assigned type
        and shapes

        Args:
            arg(str): name the process function argument you want to enforce
                checking on
            types(:obj:`tuple` of :obj:`type`): the types to restrict this
                argument to. If left as None, then no type checking will be
                done
            shapes(:obj:`tuple` of :obj:`type`):  the shapes to restrict this
                argument to. If left as None, then no shape checking will be
                done
        """
        self.types[arg] = types
        self.shapes[arg] = shapes

    ############################################################################
    #                 called by internally or by Pipeline
    ############################################################################
    def _pipeline_process(self, *data, logger, force_skip):
        """batches and processes data through the block's process function. This
        function is called by Pipeline, and not intended to be called by the
        user.

        Args:
            *data: Variable length list of data
            logger(:obj:`ImagepypelinesLogger`): parent pipeline logger, which
                will be used to create a new child block logger
            force_skip(bool): whether or not to check batch types and shapes

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
            # this separate statement is  necessary because we have to ensure
            # that process is only called once not for every data batch
            outputs = (self._make_tuple( self.process() ))
        else:
            # Note: everything is a generator until the end of this statement
            # otherwise we prepare to batch the data and run it through process
            # prepare the batch generators
            batches = (d.batch_as(self.batch_size) for d in data)
            # feed the data into the process function in batches
            # self.process(input_batch1, input_batch2, ...)
            outputs = (self._make_tuple( self.process(*self._check_batches(datums, force_skip)) ) for datums in zip(*batches))
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
    def _check_batches(self, arg_batches, force_skip):
        """checks argument batches to verify if they are the correct type and
        shapes

        NOTE:
            This could be much faster if done for the whole container instead of
            batch by batch
        """
        if force_skip or self.skip_enforcement:
            return arg_batches

        # FOR EVERY ARG AND BATCH
        # ======================================================================
        for arg_name,batch in zip(self.args, arg_batches):
            # fetch the types and shapes we'll be checking
            arg_types = self.types.get(arg_name, None)
            arg_shapes = self.shapes.get(arg_name, None)

            # NOTE: ADD CONTAINER CHECKS
            if self.batch_size == "each":
                # datums are passed in, not a container
                # there is only one datum and it's batch
                datums = (batch,)
            elif isinstance(batch, np.ndarray):
                # a container is passed in, but it's a numpy array
                # we only have to check the first row because it's an array
                datums = batch[0]
            else:
                # it's a container, and not a numpy array
                # we have to check every item in the container
                datums = batch

            # FOR EVERY DATUM IN THE BATCH
            # ==================================================================
            for datum in datums:
                # ---------------------------------------
                # TYPE CHECKING
                # ---------------------------------------
                # if arg_types is None, then we will skip all type checking
                if not (arg_types is None):
                    if not isinstance(datum, arg_types):
                        msg = "invalid type for '{}'. must be one of {}, not {}"
                        msg = msg.format(arg_name, arg_types, type(batch))
                        self.logger.error(msg)
                        raise BlockError(msg)

                # ---------------------------------------
                # SHAPE CHECKING
                # ---------------------------------------
                # if arg_shapes is None, then we will skip all shape checking
                if not (arg_shapes is None):
                    # skip shape checking if we don't have a shape_fn
                    shape_fn = self.shape_fns.get( type(datum), None )
                    if shape_fn is None:
                        continue

                    # retrieve datum shape
                    datum_shape = shape_fn(datum)

                    # FOR ARG SHAPE in all possible arg shapes
                    # ==========================================================
                    ndim_okay = False
                    for arg_shape in arg_shapes:
                        # reject automatically unless at least one shape has
                        # right number of dimensions
                        if len(arg_shape) != len(datum_shape):
                            continue

                        ndim_okay = True

                        # otherwise check every axis
                        axes_okay = True
                        for arg_ax,d_ax in zip(arg_shape,datum_shape):
                            # no need to check if the arg_ax is None (any length)
                            if arg_ax is None:
                                continue
                            # compare every axis length
                            axes_okay = (axes_okay and (arg_ax == d_ax))

                    # raise a shape error
                    if not (axes_okay and ndim_okay):
                        msg = "invalid shape for '{}'. must be one of {}, not {}"
                        msg = msg.format(arg_name, arg_shapes, datum_shape)
                        self.logger.error(msg)
                        raise BlockError(msg)

        return arg_batches

    ############################################################################
    @staticmethod
    def _make_tuple(out):
        """if the output isn't a tuple, put it in one"""
        if isinstance(out, tuple):
            return out
        return (out,)


    ############################################################################
    #                            special
    ############################################################################
    def __str__(self):
        return self.id

    ############################################################################
    def __repr__(self):
        return self.id

    ############################################################################
    def __getstate__(self):
        return self.__dict__

    ############################################################################
    def __setstate__(self, state):
        """resets the uuid in the event of a copy"""
        state['uuid'] = uuid4().hex
        self.__dict__.update(state)


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
