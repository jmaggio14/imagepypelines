# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018-2020 Jeff Maggio, Nathan Dileas, Ryan Hartzell
#
import sys
import inspect
from abc import abstractmethod
import copy
from types import FunctionType

from .Block import Block

this_module = sys.modules[__name__]

# class PipelineBlock(Block):
#     def __init__(self, pipeline):
#         self.pipeline = pipeline
#
#     def process(self, *data):
#         # we'd need to do some data checking here
#         self.pipeline.process(*data)
#
#     @property
#     def inputs(self):
#         return list(self.pipeline.inputs.keys())
#
#     @property
#     def name(self):
#         return self.pipeline.name


################################################################################
class FuncBlock(Block):
    """Block that will run anmy fucntion you give it, either unfettered through
    the __call__ function, or with optional hardcoded parameters for use in a
    pipeline. Typically the FuncBlock is only used in the `blockify` decorator
    method.

    Attributes:
        func(function): the function to call internally
        preset_kwargs(dict): preset keyword arguments, typically used for
            arguments that are not data to process
    """
    # def __new__(self, func, preset_kwargs):
    #     return type(func.__name__+"FuncBlock", (SimpleBlock,), {})

    def __init__(self, func, preset_kwargs, batch_size="singles"):
        """instantiates the function block

        Args:
            func (function): the function you desire to turn into a block
            preset_kwargs (dict): preset keyword arguments, typically used for
                arguments that are not data to process
            batch_size(str, int): the size of the batch fed into your process
                function. Must be an integer, "all", or "singles"
        """

        # JM: this is an ugly hack to make FuncBlock's serializable - by
        # adding the user's functions to the current namespace (pickle demands
        # the source object be in top level of the module)
        if not hasattr(this_module, func.__name__):
            func_copy = FunctionType(func.__code__, globals(), func.__name__)
            setattr(this_module, func_copy.__name__, func_copy)
        else:
            raise ValueError("illegal blockified function name: {}".format(func.__name__))

        self.func = func_copy
        self.preset_kwargs = preset_kwargs

        # check if the function meets requirements
        spec = inspect.getfullargspec(func)

        # we can't allow varargs at all because a block must have a known
        # number of inputs
        if (spec.varargs or spec.varkw):
            raise TypeError("function cannot accept a variable number of args")

        self._arg_spec = spec
        super().__init__(self.func.__name__, batch_size=batch_size)

    def process(self, *args):
        return self.func(*args, **self.preset_kwargs)

    def __call__(self, *args, **kwargs):
        """returns the exact output of the user defined function without any
        interference or interaction with the class
        """
        return self.func(*args,**kwargs)

    @property
    def args(self):
        """:obj:`list` of :obj:`str`: arguments in the order they are expected"""
        # save the argspec in an instance variable if it hasn't been computed
        if not self._arg_spec:
            self._arg_spec = inspect.getfullargspec(self.func)

        pos_args = ([] if (self._arg_spec.args is None) else self._arg_spec.args).copy()

        for idx,preset in enumerate(self.preset_kwargs.keys()):
            pos_args.remove(preset)

        return pos_args


################################################################################
class Input(Block):
    """An object to inject data into the graph

    Attributes:
        data(any type):
        loaded(bool): where
    """
    def __init__(self,index=None):
        """instantiates the Input

        Args:
            index(int,None): index of the input into the Pipeline
        """
        self.set_index(index)
        self.data = None
        super().__init__(name=self.name, batch_size="all")

    ############################################################################
    def process(self):
        """returns the loaded data"""
        if self.data is None:
            raise RuntimeError("data not loaded")
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
        super().__init__(self.var_name, batch_size="all")

    ############################################################################
    def process(self,*data):
        """returns the data passed in"""
        return data

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
