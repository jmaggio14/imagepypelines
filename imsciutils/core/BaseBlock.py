#
# @Email:  jmaggio14@gmail.com
#
# MIT License: https://github.com/jmaggio14/imsciutils/blob/master/LICENSE
#
# Copyright (c) 2018 Jeff Maggio, Nathan Dileas, Ryan Hartzell
#
from .Printer import get_printer
class BaseBlock(object):
    self.EXTANT = {}
    def __init__(self,
                    input_shape,
                    output_shape,
                    name=None,
                    requires_training=False,
                    setup_args=tuple(),
                    setup_kwargs={},):
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
        self.setup_args = setup_args
        self.setup_kwargs = setup_kwargs

        self.trained = False
        if not self.requires_training:
            self.trained = True

        self.printer = get_printer(self.name)

    def setup(self,*args,**kwargs):
        pass

    def train(self,batch_data,batch_labels=None):
        pass

    def before_process(batch_data,batch_labels=None):
        pass

    def after_process(self):
        pass

    def _pipeline_train(self,batch_data,batch_labels=None):
        self.train(self,batch_data,batch_labels)
        self.trained = True


class SimpleBlock(BaseBlock):
    def process(self,datum):
        raise NotImplementedError("'process' must be overloaded in all children")

    def label(lbl):
        return lbl

    def _pipeline_process(self,batch_data,batch_labels=None):
        if batch_labels is None:
            batch_labels = [None] * len(batch_data)

        #running prep function
        self.before_process(batch_data,batch_labels)

        # processing data
        processed = [self.process(datum) for datum in batch_data]
        labels = [self.label(lbl) for lbl in batch_labels]

        # running post-process / cleanup function
        self.after_process()

        return processed, labels

class BatchBlock(BaseBlock):
    def batch_process(self,batch_data):
        raise NotImplementedError("'batch_process' must be overloaded in all children")

    def batch_labels(batch_labels):
        return batch_labels

    def _pipeline_process(self,batch_data,batch_labels=None):
        if batch_labels is None:
            batch_labels = [None] * len(batch_data)

        #running prep function
        self.before_process(batch_data,batch_labels)

        # processing data
        processed = self.batch_process(batch_data)
        labels = self.batch_labels(batch_labels)

        # running post-process / cleanup function
        self.after_process()

        return processed, labels


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
