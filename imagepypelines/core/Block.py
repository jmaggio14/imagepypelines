# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018-2020 Jeff Maggio, Ryan Hartzell, and collaborators
from ..Logger import get_logger
from ..Logger import ImagepypelinesLogger
from .constants import NUMPY_TYPES, UUID_ORDER
from .Exceptions import BlockError
from .arg_checking import DEFAULT_SHAPE_FUNCS, HOMOGENUS_CONTAINERS
from .Data import is_container

from uuid import uuid4
from abc import ABCMeta, abstractmethod
from itertools import chain
import inspect
import copy
import numpy as np

class Block(metaclass=ABCMeta):
    """a contained algorithmic element used to construct pipelines. This class
    is designed to be inherited from, or used in the form of one of its child
    classes.

    Note:
        you must overload `Block.process()` if you intend to inherit from this
        class

    Attributes:
        uuid(str): hex uuid for this pipeline
        name(str): user specified name for this pipeline, used to generate
            the unique id. defaults to the name of your subclass
        batch_type(str, int): the size of the batch fed into your process
            function. Will be an integer, "all", or "each"
        void(bool): Boolean value. By default all blocks return a value or
            values as output. However, if printing to screen, plotting, or
            saving data to a file, a block may not have a meaningful output
            that should be stored in a pipeline's output dictionary. In this
            case, void should be set to True, so that the output of the block
            is ignored. The associated var key in the pipeline output will
            contain a value of :obj:`None`.
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
        containers(:obj:`dict`): Dictionary of input containers. If arg doesn't
            exist as a key, or if the value is None, then no checking is done
            *if batch_type is "each", then the container is irrelevant and can
            be safely ignored!*
        shape_fns(:obj:`dict`): Dictionary of shape functions to retrieve. If
            type(arg_datum) doesn't exist as a key, or if the value is None,
            then no checking is done.
    """
    def __init__(self,
                    name=None,
                    batch_type="all",
                    types=None,
                    shapes=None,
                    containers=None,
                    void=False):
        """instantiates the block

        Args:
            name(str,None): the name of this block - how it will show up in the
                graph.
            batch_type(str, int): the type of the batch processing for your
                process function. Either "all" or "each". "all" means that all
                argument data will be passed into to your function at once,
                "each" means that each argument datum will be passed in
                individually
            types(:obj:`dict`,None): Dictionary of input types. If arg doesn't
                exist as a key, or if the value is None, then no checking is
                done. If not provided, then will default to args as keys, None
                as values.
            shapes(:obj:`dict`,None): Dictionary of input shapes. If arg doesn't
                exist as a key, or if the value is None, then no checking is
                done. If not provided, then will default to args as keys, None
                as values.
            containers(:obj:`dict`,None): Dictionary of input containers. If arg
                doesn't exist as a key, or if the value is None, then no
                checking is done. If not provided, then will default to args as
                keys, None as values.
                *if batch_type is "each", then the container is irrelevant and can
                be safely ignored!*
            void(bool): Boolean value. By default all blocks return a value or
                values as output. However, if printing to screen, plotting, or
                saving data to a file, a block may not have a meaningful output
                that should be stored in a pipeline's output dictionary. In this
                case, void should be set to True, so that the output of the block
                is ignored. The associated var key in the pipeline output will
                contain a value of :obj:`None`. Default is False
        """
        assert batch_type in ("all","each"),"batch_type must be 'each' or 'all'"

        # setup absolutely unique id for this block
        self.uuid = uuid4().hex

        # ------ setting up instance variables
        if name is None:
            name = self.__class__.__name__
        self.name = name
        self.batch_type = batch_type
        self._void = void

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

        # containers
        if containers is None:
            self.containers = {arg : None for arg in self.args}
        else:
            if not isinstance(containers,dict):
                raise TypeError("'containers' must be a dictionary or None")
            self.containers = containers

        self.shape_fns = DEFAULT_SHAPE_FUNCS.copy()

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
    def preprocess(self):
        """runs before all batches are processed"""
        pass

    ############################################################################
    def postprocess(self):
        """runs after

         all batches are processed"""
        pass


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
    def enforce(self, arg, types=None, shapes=None, containers=None):
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
            containers(:obj:`tuple` of :obj:`type`):  the containers to restrict
                this argument to. If left as None, then no container checking
                will be done.
                *if batch_type is "each", then the container is irrelevant and
                can be safely ignored!*

        Returns:
            :obj:`Block` : self

        Note:
            This function must be called after the parent block is instantiated!

            That is, in your `__init__` function, you must call
            `super().__init__` before calling `self.enforce`
        """
        # make sure the parent block object is already instantiated before we
        # run this function (i.e. call super().__init__ before enforcement)
        if not hasattr(self, 'uuid'):
            raise BlockError("Block __init__ must be called before enforcement")

        # NOTE: force values to be lists of lists/None (ie add error checking)
        self.types[arg] = types
        self.shapes[arg] = shapes
        self.containers[arg] = containers

        return self

    ############################################################################
    #                 called internally or by Pipeline
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

        # run preprocess
        self.preprocess()

        # root blocks don't need input data, and won't have any data
        # passed in to batch. We only call process once for these
        if self.n_args == 0:
            # this separate statement is  necessary because we have to ensure
            # that process is only called once not for every data batch
            # (only if there are no inputs, ie no batches, into this block)
            ret = self.process()
            # put it a tuple if it isn't already
            if not isinstance(ret, tuple):
                ret = (ret, )

        else:
            # --------- CHECKING  ---------
            # check the batches before processing
            if not (force_skip or self.skip_enforcement):
                self._check_batches(*data)

            # --------- ACTUAL PROCESSING ---------
            # EACH - every batch is a datum
            if self.batch_type == "each":
                # construct the batch generators
                def _process_batches(*data):
                    batches = (d.as_each() for d in data)
                    for datums in zip(*batches):
                        out = self.process(*datums)
                        # put it a tuple if it isn't already
                        if not isinstance(out, tuple):
                            out = (out, )
                        yield out

                ret = tuple( zip(*_process_batches(*data)) )

            # ALL - process everything at once
            else: # if batch_type == "all"
                batches = (d.as_all() for d in data)
                ret = self.process(*batches)

                # if there is a return value for this block (most blocks)
                # we make sure we can write this data to a graph edge
                if not self._void:
                    # put it a tuple if it isn't already
                    if not isinstance(ret, tuple):
                        ret = (ret, )

                    # enforce container outputs on batch_type="all" blocks
                    for i,out in enumerate(ret):
                        if not is_container(out):
                            msg = "Blocks with batch_type='all' must return containers of data (output %s is '%s', which is not an iterable type) or have their 'void' attribute set to 'True'. "
                            msg = msg % (i, type(out))
                            self.logger.error(msg)
                            raise BlockError(msg)

        self.postprocess()
        return ret

    ############################################################################
    def _check_batches(self, *data):
        """checks argument batches to verify if they are the correct type and shapes
        """
        all_data = (d.as_all() for d in data)
        # FOR EVERY ARG AND BATCH
        # ======================================================================
        for arg_name,data_container in zip(self.args, all_data):
            # ---------- CONTAINER CHECK ----------
            # we have to check the container if datums aren't passed in individually
            if self.batch_type == "all":
                okay_containers = self.containers.get(arg_name,None)
                if okay_containers is not None:
                    # check the container type is valid
                    if not isinstance(data_container, okay_containers):
                        msg = "invalid container for '{}'. must be {}, not {}. (you can disable this check with the 'skip_enforcement' keyword)"
                        msg = msg.format(arg_name, okay_containers, type(batch))
                        self.logger.error(msg)
                        raise BlockError(msg)


            # check if it's a homogenus container
            # for example if it's a numpy array, we can speed thing sup because
            # we only have to check the first row
            if type(data_container) in HOMOGENUS_CONTAINERS:
                data_container = data_container[0]


            # FOR EVERY DATUM IN THE CONTAINER
            # ==================================================================
            for datum in data_container:
                # ---------------------------------------
                # TYPE CHECKING
                # ---------------------------------------
                # fetch the accepted types for this arg
                arg_types = self.types.get(arg_name, None)
                # if arg_types is None, then we will skip all type checking
                if not (arg_types is None):
                    if not isinstance(datum, arg_types):
                        msg = "invalid type for '{}'. must be {}, not {}. (you can disable this check with the 'skip_enforcement' keyword)"
                        msg = msg.format(arg_name, arg_types, type(batch))
                        self.logger.error(msg)
                        raise BlockError(msg)

                # ---------------------------------------
                # SHAPE CHECKING
                # ---------------------------------------
                # fetch the accepted shapes for this arg
                arg_shapes = self.shapes.get(arg_name, None)
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
                    axes_okay = True
                    for arg_shape in arg_shapes:
                        # reject automatically unless at least one shape has
                        # right number of dimensions
                        if len(arg_shape) != len(datum_shape):
                            continue

                        ndim_okay = True

                        # otherwise check every axis
                        for arg_ax,d_ax in zip(arg_shape,datum_shape):
                            # no need to check if the arg_ax is None (any length)
                            if arg_ax is None:
                                continue
                            # compare every axis length
                            axes_okay = (axes_okay and (arg_ax == d_ax))

                    # raise a shape error
                    if not (axes_okay and ndim_okay):
                        msg = "invalid shape for '{}'. must be {}, not {}"
                        msg = msg.format(arg_name, arg_shapes, datum_shape)
                        self.logger.error(msg)
                        raise BlockError(msg + " (you can disable this check with the 'skip_enforcement' keyword)")


    ############################################################################
    def _summary(self):
        """fetches a static summary of the block"""
        summary = {}

        # instance vars
        summary['name'] = self.name
        summary['id'] = self.id
        summary['uuid'] = self.uuid
        summary['args'] = self.args
        summary['types'] = self.types
        summary['shapes'] = self.shapes
        summary['skip_enforcement'] = self.skip_enforcement
        summary['batch_type'] = self.batch_type
        summary['tags'] = list(self.tags)

        # other data
        summary['class_name'] = self.__class__.__name__

        # method documentation
        summary['DOCS'] = {}
        summary['DOCS']['class'] = inspect.getdoc(self)
        summary['DOCS']['__init__'] = inspect.getdoc(self.__init__)
        summary['DOCS']['process'] = inspect.getdoc(self.process)

        return summary

    ############################################################################
    def get_default_node_attrs(self):
        """all values must be json serializable"""
        attrs = { 'name':self.name,
                'color': 'orange',
                'shape':'square',
                'class_name': str( type(self) ),
                'batch_type': self.batch_type,
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
        """int: Number of arguments for the process function"""
        return len(self.args)

    ############################################################################
    @property
    def id(self):
        """str: A unique id for this block

        This id is a combination of the block's non-unique name and
        part of it's uuid (last 6 characters by default).
        The entropy of this id can be increased by increasing ImagePypelines
        UUID_ORDER variable
        """
        return "{}#{}".format(self.name, self.uuid[-UUID_ORDER:])

    ############################################################################
    @property
    def void(self):
        """bool: Represents whether or not the block has a void output"""
        return self._void

    @void.setter
    def void(self, val):
        """
        Setter for the 'void' property of this block
        """

        if (val==1) or (val==0) or (val==True) or (val==False):

            self._void = val

        else:

            msg = "'Void' only takes boolean values."
            self.logger.error(msg)
            raise AttributeError(msg + "You specified a value of {}".format(val))

# END
