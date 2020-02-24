# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018-2019 Jeff Maggio, Nathan Dileas, Ryan Hartzell
#
from .block_subclasses import FuncBlock


def blockify(**kwargs):
    """decorator which converts a normal function into a un-trainable
    block which can be added to a pipeline. The function can still be used
    as normal after blockification (the __call__ method is setup such that
    unfettered access to the function is permitted)

    Example:
        >>> import imagepypelines as ip
        >>>
        >>> @ip.blockify(value=10)
        >>> def add_value(datum, value):
        ...    return datum + value
        >>>
        >>> type(add_value)
        <class 'FuncBlock'>

    Args:
        **kwargs: hardcode keyword arguments for a function, these arguments
            will not have to be used to

    """
    def _blockify(func):
        return FuncBlock(func,kwargs)
    return _blockify


################################################################################
#                                CLASSES
################################################################################

# DO NOT DELETE!!! - may be useful in future
# class Data(object):
#     def __init__(self,data):
#         self.data = data
#         if isinstance(data, np.ndarray):
#             self.type = "array"
#         elif isinstance(data, (list,tuple)):
#             self.type = "iter"
#         else:
#             self.type = "iter"
#             self.data = [self.data]
#
#     def batch_data(self):
#         return self.data
#
#     def datums(self):
#         if self.type == "iter":
#             for d in self.data:
#                 yield d
#
#         elif self.type == "array":
#             # return every row of data
#             for r in range(self.data.shape[0]):
#                 yield self.data[r]
#
#     def __iter__(self):
#         return self.datums()
