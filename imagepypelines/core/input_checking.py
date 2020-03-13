from abc import ABCMeta, abstractmethod
from .Exceptions import InputTypeError

# PLACEHOLDERS until I write the real functions
register_container(container)
register_input_type(obj, shape_fn)

# define the base container class
class BaseContainer(metaclass=ABCMeta):
    @abstractmethod
    def __len__(self):
        pass

    @abstractmethod
    def __getitem__(self, idx):
        pass

    @abstractmethod
    def __getslice__(self, slice):
        pass


class ArgType(object):
    def __init__(self, shapes, containers):
        """instantiates the ArgType

        Args:
            shape(tuple,list): list or tuple of data shapes
            containers(tuple,list): list or tuple of containers
        """
        self.shapes = shapes
        self.containers = containers

def batch_check(self, *batches):
    # batches is a single datum
    sorted_type_fns = [input_types[k] for k in self.args]
    if self.batch_size = "singles":






# class BatchChecker(object):
#     """checks to make sure the"""
#     def __init__(self, dtype, shape):
#         # force shape to be a list or tuple
#         if not isinstance(shape, (list,tuple)):
#             raise RuntimeError("'shape' must be a tuple or list")
#
#         # instance variables
#         self.dtype = dtype
#         self.shape = shape
#         self.length = len(shape)
#
#     ####################################################################
#     def shape_check(self, input_shape):
#         if len(input_shape) != self.length:
#             raise InputTypeError("Block requires shape '%s', but got '%s'" % self.shape, input_shape)
#
#         # check to make sure every axis is compatible
#         if not all( map(self.axis_check, zip(self.shape,input_shape)) ):
#             raise InputTypeError("Block requires shape '%s', but got '%s'" % self.shape, input_shape)
#
#     ####################################################################
#     def type_check(self, other):
#         if not isinstance(other, self.dtype):
#             raise InputTypeError("Block Requires '%s', but got '%s'" % (self.dtype, type(other)))
#
#     ####################################################################
#     @staticmethod
#     def axis_check(shape_axis, input_axis):
#         if shape_axis is None:
#             return True
#         return (shape_axis == input_axis)
#
# ########################################################################
#
# class BaseInputType(object):
#     def __init__(self, shape):
#         self.shape = shape
#         self.shape_fn = shape_fn
#
# """
# "singles" In which it calls process once for every datum
#
# in a list this means it calls process for every list element
#
# in the case of an array, this means it passes in every row of the array
# into the block
#     so I had a stack of images (num_images, H, W, C), then process would
#     be called num_image times where each call it passes in an Array
#     of shape (H,W,C)
#
# """
# """
# "all" in which all data is passed in to the block at once
#
# in a list this means the entire list is passed in
#
# in an array, the entire array is passed in.
#     so I had a stack of images (num_images, H, W, C), then process would
#     be called once with an input of shape (num_images, H, W, C)
# """
#
# """
# and of course batch_size = <int> where a subsection of the data is passed in
#
# in a list this means a slice of batch_size is passed in
#
# in an array, a substack of batch_size is passed in
#     so I had a stack of images (num_images, H, W, C), then process would
#     be called ceil(num_images/batch_size) times with an input of shape (batch_size, H, W, C)
#
#
# """
#
#
# class InputTypeFactory(object):
#
#     def __init__(self, obj, shape_fn):
#         self.obj = obj
#         self.shape_fn = shape_fn
#
#
#
# input_types = [Array([None,None,3])]
#
#
#
#
#
#
#
# # class Array(InputType):
# #     def inpect(self):
# #         return self.datum.shape
# #
# #     def shape_check(self, expected):
