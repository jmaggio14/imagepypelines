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

from .BaseBlock import BaseBlock

class SimpleBlock(BaseBlock):
    """Block subclass that processes individual datums separately
    (as opposed to processing all data at once in a batch). This makes it useful
    for most CPU bound processing tasks as well as most functions in traditional
    computer vision that don't require an image sequence to process data

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

        io_map(IoMap): object that maps inputs to this block to outputs
            subclass of tuple where I/O is stored as:
            ( (input1,output1),(input2,output2)... )
        name(str): unique name for this block
        notes(str): a short description of this block
        requires_training(bool): whether or not this block will require
            training
        trained(bool): whether or not this block has been trained, True
            by default if requires_training = False
        logger(ip.ImagepypelinesLogger): logger for this block,
            registered to 'name'

    """

    @abstractmethod
    def process(self, *datum):
        """(required overload)processes a single datum

        Args:
            datum: datum to process

        Returns:
            processed: datum processed by this block
        """
        raise NotImplementedError("'process' must be overloaded in all children")

    def process_strategy(self, *data):
        """processes each datum using self.process and return list"""
        output = (self.process(*datums) for datums in zip(*data))
        return tuple( zip(*output) )

    @property
    def inputs(self):
        # save the argspec in an instance variable if it hasn't been computed
        if not self._arg_spec:
            self._arg_spec = inspect.getfullargspec(self.process)

        return ([] if (self._arg_spec.args is None) else self._arg_spec.args[1:])


################################################################################
class BatchBlock(BaseBlock):
    """Block subclass that processes datums as a batch
    (as opposed to processing each datum individually). This makes it useful
    for GPU accelerated tasks where processing data in batches frequently
    increases processing speed. It can also be used for algorithms that
    require working with a full image sequence.

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

        io_map(IoMap): object that maps inputs to this block to outputs
            subclass of tuple where I/O is stored as:
            ( (input1,output1),(input2,output2)... )
        name(str): unique name for this block
        notes(str): a short description of this block
        requires_training(bool): whether or not this block will require
            training
        trained(bool): whether or not this block has been trained, True
            by default if requires_training = False
        logger(ip.ImagepypelinesLogger): logger for this block,
            registered to 'name'

    """

    @abstractmethod
    def batch_process(self, *data):
        """(required overload)processes a list of data using this block's
        algorithm

        Args:
            data(list): list of datums to process

        Returns:
            process(list): list of processed datums
        """
        error_msg = "'batch_process' must be overloaded in all children"
        raise NotImplementedError(error_msg)

    def process_strategy(self, *data):
        """runs self.batch_process"""
        return self.batch_process(*data)

    @property
    def inputs(self):
        # save the argspec in an instance variable if it hasn't been computed
        if not self._arg_spec:
            self._arg_spec = inspect.getfullargspec(self.batch_process)

        return ([] if (self._arg_spec.args is None) else self._arg_spec.args[1:])


################################################################################
class FuncBlock(SimpleBlock):
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

    def __init__(self,func, preset_kwargs):
        self.func = func
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
        super().__init__(self.func.__name__)

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
    def inputs(self):
        # save the argspec in an instance variable if it hasn't been computed
        if not self._arg_spec:
            self._arg_spec = inspect.getfullargspec(self.func)

        return ([] if (self._arg_spec.args is None) else self._arg_spec.args)



################################################################################
class Input(BatchBlock):
    def __init__(self,index_key=None):
        self.index_key = index_key
        # DEBUG
        # eventually we will be able to specify inputs using
        # END DEBUG
        self.data = None
        super().__init__(name="Input"+str(self.index_key))

    def batch_process(self):
        return self.data

    def load(self, data):
        self.data = data

    def unload(self, data):
        self.data = None

################################################################################
class Leaf(BatchBlock):
    def __init__(self,var_name):
        self.var_name = var_name
        super().__init__(self.var_name)

    def batch_process(self,*data):
        return data

    @property
    def inputs(self):
        return [self.var_name]

# END
