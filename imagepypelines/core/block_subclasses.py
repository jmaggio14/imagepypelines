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

    Args:
        func (function): the function you desire to turn into a block
        preset_kwargs (dict): preset keyword arguments, typically used for
            arguments that are not data to process
    """
    # def __new__(self, func, preset_kwargs):
    #     return type(func.__name__+"FuncBlock", (SimpleBlock,), {})

    def __init__(self, func, preset_kwargs, batch_size="singles"):

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

        num_required = len(spec.args) - len(preset_kwargs)
        required = spec.args[:num_required]

        self._arg_spec = spec
        super().__init__(self.func.__name__, batch_size=batch_size)

    def process(self, *args):
        return self.func(*args, **self.preset_kwargs)

    def __call__(self,*args,**kwargs):
        """returns the exact output of the user defined function without any
        interference or interaction with the class
        """
        return self.func(*args,**kwargs)

    def __str__(self):
        return self.func.__name__+"FuncBlock"

    @property
    def args(self):
        # save the argspec in an instance variable if it hasn't been computed
        if not self._arg_spec:
            self._arg_spec = inspect.getfullargspec(self.func)

        return ([] if (self._arg_spec.args is None) else self._arg_spec.args)


################################################################################
class Input(Block):
    def __init__(self,index=None):
        self.set_index(index)
        self.data = None
        self.loaded = False
        super().__init__(name=self.name, batch_size="all")

    def process(self):
        if self.data is None:
            raise RuntimeError("data not loaded")
        return self.data

    def load(self, data):
        self.data = data
        self.loaded = True

    def unload(self):
        self.data = None
        self.loaded = False

    def get_default_node_attrs(self):
        attrs = super().get_default_node_attrs()
        attrs['color'] = 'blue'
        attrs['shape'] = 'pentagon'
        return attrs

    def set_index(self,index):
        self.index = index
        self.name = "Input" + str(self.index)

################################################################################
class Leaf(Block):
    def __init__(self,var_name):
        self.var_name = var_name
        super().__init__(self.var_name, batch_size="all")

    def process(self,*data):
        return data

    @property
    def inputs(self):
        return [self.var_name]

    def get_default_node_attrs(self):
        attrs = super().get_default_node_attrs()
        attrs['color'] = 'green'
        attrs['shape'] = 'ellipsis'
        return attrs

# END
