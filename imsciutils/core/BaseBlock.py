#
# @Email:  jmaggio14@gmail.com
#
# MIT License: https://github.com/jmaggio14/imsciutils/blob/master/LICENSE
#
# Copyright (c) 2018 Jeff Maggio, Nathan Dileas, Ryan Hartzell
#
from .Printer import get_printer
def create_lazy_block(processing_fn,
                        input_shape=None,
                        output_shape=None,
                        process_group=False,
                        name=None,
                        args=tuple(),
                        kwargs={}):

    # making the process_fn static so it can operate inside of a class
    process_fn = staticmethod(processing_fn)
    # create a new block using a metaclass instance
    block_cls = type(processing_fn.__name__,
                        (BaseBlock,),
                        {'process_fn':process_fn})

    block = block_cls(input_shape=input_shape,
                        output_shape=output_shape,
                        name=name,
                        process_group=process_group,
                        requires_training=False, #JM: func is only for lazy blocks
                        args=args,
                        kwargs=kwargs)
    return block

# class Transfer(object):
#     def __init__(self,shape,):
#         self.shape = shape
#
#     def compatible(self,shape):
#         return self.shape == shape

class BaseBlock(object):
    self.EXTANT = {}
    def __init__(self,
                    input_shape,
                    output_shape,
                    name,
                    process_group=False,
                    requires_training=False,
                    args=tuple(),
                    kwargs={},):
        # ----------- building a unique name for this block ------------
        if name is None:
            name = self.__class__.__name__

        # keeping track of names in base class variable
        if name in self.EXTANT:
            self.EXTANT[name] += 1
        else:
            self.EXTANT[name] = 1
        name = name + str(self.EXTANT[name])

        self.input_shape = input_shape
        self.output_shape = output_shape
        self.process_group = process_group
        self.name = name
        self.requires_training = requires_training
        self.args = args
        self.kwargs = kwargs

        self.trained = False
        if not self.requires_training:
            self.trained = True

        self.printer = get_printer(self.name)

    def process_fn(self,data,*args,**kwargs):
        raise NotImplementedError("'process_fn' must be overloaded")

    def train(self,x_data):
        pass

    def run_train(self,x_data):
        self.train(x_data)
        self.trained = True

    def run_process(self,x_data):
        if not self.trained:
            error_msg = "'{}' must be trained before processing can occur"\
                        .format(self.name)
            raise RunTimeError(error_msg)

        if process_group:
            out = self.process_fn(x_data,*self.args,**self.kwargs)
        else:
            out = [self.process_fn(d,*self.args,**self.kwargs) for d in x_data]
        return out




#
#
#
#
# class BaseBlock(object):
#     """Base processing block object for constructing image processing pipelines
#
#     This object is meant to be subclassed for use in creating blocks for
#     use in `imsciutils` Pipeline objects.
#
#     Args:
#         name (str): the name of this block, default will be the name of the class
#
#     """
#     extant = {}
#     def __init__(self, name=None):
#         # JM: making printer for this class
#         if name is None:
#             name = self.__class__.__name__
#
#         # keeping track of names internally in a class variable
#         if name in self.extant:
#             self.extant[name] += 1
#         else:
#             self.extant[name] = 1
#         name = name + str(self.extant[name])
#
#         self.name = name
#         self.printer = get_printer(name)
#         self.is_trained = False
#
#     def setup(self, **kwargs): #setups the special arguments for this block
#         """(Optional overload)checks the instantiation kwargs
#
#         Function to overload to check the instantiation keywords for this
#         processing block. This function is meant to replace the __init__
#         function
#
#         Args:
#             kwargs (dict): dictionary of kwargs passed into __init__ to set up
#
#         Returns:
#             self: this function must return self
#
#         Example:
#             def setup(param1,param2='example'):
#                 self.param1 = param1
#                 self.param2 = param2
#         """
#         raise NotImplementedError("'setup' must be overloaded in all Block children") #setups the special arguments for this block
#
#     def train(self, x_data): #trains the feature generator if required
#         """(Optional overload)trains this processing block
#
#         If this processing block requires training, this function can be
#         overloaded to train the underlying algorithm
#
#         Args:
#             x_data (variable type): training data for this processing block
#
#         Returns:
#             None
#         """
#         pass
#
#     def process(self, x_data): # applies the algorithm to the data
#         """(Required overload)applys this blocks algorithm to the input data
#
#         Applies this blocks algorithm to the input data and returns the
#         processed data
#
#         Args:
#             x_data (type specified in validate_data): the input data to apply
#                 the algorithm too
#
#         Returns:
#             processed_data
#         """
#         raise NotImplementedError("'process' must be overloaded in all Block children")
#
#     def validate_data(x_data):#validates input data
#         """(Optional overload)validates the data is of the correct type
#
#         This function should be overloaded to check and make sure the input data
#         is of the correct type and shape such that this block won't throw a
#         nebulous error. This function is expected to throw an error if the
#         input data is invalid.
#         The primary purpose of this function is for traceability purposes so
#         that errors in pipeline construction can be easily tracked to their
#         genesis
#
#         Args:
#             x_data (input datatype): the input data to validate
#
#         Raises:
#             user defined error
#         """
#         pass
#
#     def run_train(self, x_data):#JM: only called by Pipeline
#         """convienence function to validate input data and train the block"""
#         self.validate_data(x_data)
#         self.train(x_data)
#         self.is_trained = True
#
#     def run_process(self, x_data): #JM: only called by Pipeline
#         """convienence function to validate input data and process the data"""
#         if not self.is_trained:
#             error_msg = "the block must be trained before processing"
#             self.printer.error(error_msg)
#             raise RuntimeError(error_msg)
#
#         self.validate_data(x_data)
#         return self.process(x_data)
#
#
#
#
#
#
#
# # end
