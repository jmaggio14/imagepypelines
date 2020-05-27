# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018-2020 Jeff Maggio, Ryan Hartzell, and collaborators
#
import sys
import inspect
from abc import abstractmethod
import copy
from types import FunctionType
from functools import wraps

from .Block import Block
from . import func_namespace


################################################################################
class PipelineBlock(Block):
    """Block which runs a pipeline internally (used for nesting pipelines
    within pipelines)

    Attributes:
        pipeline(:obj:`Pipeline`): pipeline to process with
        fetch(:obj:`tuple` of :obj:`str`): variables to fetch from the pipeline
            in the order to retrieve them in

    Batch Size:
        "each"
    """
    def __init__(self, pipeline, fetch):
        """instantiates the PipelineBlock

        Args:
            pipeline(:obj:`Pipeline`): pipeline to process with
            fetch(:obj:`tuple` of :obj:`str`): variables to fetch from the
                pipeline in the order to retrieve them in
        """
        # check to make sure all the fetch vars are actually in the pipeline
        if not all((fet in pipeline.vars) for fet in fetch):
            msg = "Invalid Pipeline fetch, must be one of %s" % pipeline.vars.keys()
            raise BlockError(msg)

        # instantiate block args
        self.fetch = fetch
        self.pipeline = pipeline
        # NOTE: do something here to support arg checking for the pipeline!!!

        super().__init__(name=pipeline.name, batch_type="all")


    ############################################################################
    def process(self, *args):
        """Runs the pipeline and fetches the desired variables"""
        # NOTE: we might want to make the pipeline's logger a child of this
        # block's logger in here?
        processed = self.pipeline.process(*args, fetch=self.fetch)

        # turn processed dict into a tuple of fetches
        return tuple(processed[fet] for fet in self.fetch)

    ############################################################################
    @property
    def args(self):
        """:obj:`list` of :obj:`str`: arg names for the pipeline"""
        return self.pipeline.args


################################################################################
class FuncBlock(Block):
    """Block that will run any function you give it, either unfettered through
    the __call__ function, or with optional hardcoded parameters for use in a
    pipeline. Typically the FuncBlock is only used in the :obj:`blockify`
    decorator method.

    Attributes:
        func(function): the function to call internally
        preset_kwargs(dict): preset keyword arguments, typically used for
            arguments that are not data to process
    """
    def __new__(cls, func, preset_kwargs={}, **block_kwargs):
        """Generates the new function block

        Args:
            func (function): the function you desire to turn into a block
            preset_kwargs (dict): preset keyword arguments, typically used for
                arguments that are not data to process
            **block_kwargs: keyword arguments for :obj:`Block` instantiation
        """
        obj = super().__new__(cls)
        obj.namespace_key = str( id(obj) )

        # copy the method to avoid and any possible edge-case weirdness
        func = copy.copy(func)
        # make the func a staticmethod if it isn't already
        # next line checks if it's not a staticmethod
        if isinstance(func, FunctionType):
            # set the object in the funcblock namespace so it can be pickled
            vars(func_namespace)[obj.namespace_key] = func
            # sets class attributes with metadata that won't be available
            # in a staticmethod
            obj.func_name = func.__name__
            obj._arg_spec = inspect.getfullargspec(func)
            func = staticmethod( func )
            # import pdb; pdb.set_trace()
        else:
            # these will be set later by pickle or the copy module,
            # (see __deepcopy__ for more info)
            obj.func_name = None
            obj._arg_spec = None

        obj.func = func
        obj.preset_kwargs = preset_kwargs

        return obj

    def __init__(self, func, preset_kwargs={}, **block_kwargs):
        """instantiates the function block

        Args:
            func (function): the function you desire to turn into a block
            preset_kwargs (dict): preset keyword arguments, typically used for
                arguments that are not data to process
            **block_kwargs: keyword arguments for :obj:`Block` instantiation
        """
        # we can't allow varargs at all because a block must have a known
        # number of inputs
        if (self._arg_spec.varargs or self._arg_spec.varkw):
            raise TypeError("function cannot accept a variable number of args")

        super().__init__(self.func_name, **block_kwargs)

    def process(self, *args):
        # reference the original function as staticmethods aren't callable when unbound
        return self.func.__func__(*args, **self.preset_kwargs)

    def __call__(self, *args, **kwargs):
        """returns the exact output of the user defined function without any
        interference or interaction with the class
        """
        return self.func.__func__(*args,**kwargs)

    @property
    def args(self):
        """:obj:`list` of :obj:`str`: arguments in the order they are expected"""
        # save the argspec in an instance variable if it hasn't been computed
        pos_args = ([] if (self._arg_spec.args is None) else self._arg_spec.args).copy()

        for idx,preset in enumerate(self.preset_kwargs.keys()):
            pos_args.remove(preset)

        return pos_args


    def __deepcopy__(self, memo):
        # NOTE: this behavior assumes that the uuid will be updated outside
        # this function (as occurs in Block.copy() and Block.deepcopy())
        cls = self.__class__
        # create a new block - note that func isn't actually copied
        new_block = cls.__new__(cls, self.func, self.preset_kwargs)
        memo[id(self)] = new_block
        for k,v in self.__dict__.items():
            # don't copy values already set in the class by __new__
            if (k == "func") or (k == "preset_kwargs"):
                continue
            setattr(new_block, k, copy.deepcopy(v,memo))


        return new_block

################################################################################
class Input(Block):
    """An object to inject data into the graph

    Attributes:
        data(any type):
        loaded(bool): where
    """
    def __init__(self, index=None):
        """instantiates the Input

        Args:
            index(int,None): index of the input into the Pipeline
        """
        self.set_index(index)
        self.data = None
        super().__init__(name=self.name, batch_type="all")

    ############################################################################
    def process(self):
        """returns the loaded data"""
        if self.data is None:
            msg = "data not loaded"
            self.logger.error(msg)
            raise RuntimeError(msg)
        return self.data

    ############################################################################
    def load(self, data):
        """loads the given data for distribution into the pipeline"""
        self.data = data

    ############################################################################
    def unload(self):
        """unloads the data"""
        self.data = None

    ############################################################################
    def get_default_node_attrs(self):
        """retrieves default node attributes for the Input"""
        attrs = super().get_default_node_attrs()
        attrs['color'] = 'blue'
        attrs['shape'] = 'pentagon'
        return attrs

    ############################################################################
    def set_index(self, index):
        """sets the input index"""
        self.index = index
        self.name = "Input" + str(self.index)


    ############################################################################
    #                               properties
    ############################################################################
    @property
    def loaded(self):
        """bool: whether or not data has been loaded"""
        return (self.data is not None)

################################################################################
class Leaf(Block):
    """a block to act as a leaf node in the Pipeline Graph. Used to complete
    final outgoing edges from processing blocks

    Attributes:
        var_name(str): the name of the variable this leaf represents
    """
    def __init__(self,var_name):
        """instantiates the leaf

        Args:
            var_name(str): the name of the variable this leaf represents
        """
        self.var_name = var_name
        super().__init__(self.var_name, batch_type="all")

    ############################################################################
    def process(self,*data):
        """does nothing in a leaf"""
        pass
        # return data

    ############################################################################
    def _pipeline_process(self,*data, **kwargs):
        return data[0]

    ############################################################################
    def get_default_node_attrs(self):
        """retrieves default node attributes for the Leaf"""
        attrs = super().get_default_node_attrs()
        attrs['color'] = 'green'
        attrs['shape'] = 'ellipsis'
        return attrs

    ############################################################################
    #                               properties
    ############################################################################
    @property
    def args(self):
        """:obj:`list` of :obj:`str`: returns a 1-element list for this leaf's input"""
        return [self.var_name]


# END
