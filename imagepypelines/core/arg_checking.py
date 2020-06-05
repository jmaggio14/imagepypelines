# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018 - 2020 Jeff Maggio, Jai Mehra, Ryan Hartzell
#
import numpy as np

################################################################################
# np.ndarray
def numpy_shape(obj):
    """retrieves the shape of numpy - array.shape"""
    return obj.shape

################################################################################
# int
def int_shape(obj):
    """retrieves the shape of int - None"""
    return None

################################################################################
# float
def float_shape(obj):
    """retrieves the shape of float - None"""
    return None

################################################################################
# list
def list_shape(obj):
    """retrieves the shape of list - (len(list),)"""
    return (len(obj),)

################################################################################
# tuple
def tuple_shape(obj):
    """retrieves the shape of tuple - (len(tuple),)"""
    return (len(obj),)

################################################################################
# str
def str_shape(obj):
    """retrieves the shape of str - (len(str),)"""
    return (len(obj),)

################################################################################
# dict
def dict_shape(obj):
    """retrieves the shape of dict - (len(dict),)"""
    return (len(obj),)

######## For actual pre-process shape check logic ####
DEFAULT_SHAPE_FUNCS = {np.ndarray : numpy_shape,
                                int : int_shape,
                                float : float_shape,
                                list : list_shape,
                                tuple : tuple_shape,
                                str : str_shape,
                                dict : dict_shape,
                            }
"""default shape functions built into core ImagePypelines. Keys are
types, values are functions to that return a shape tuple"""

SHAPE_FUNCS = DEFAULT_SHAPE_FUNCS.copy()
"""functions to determine the shape of a datum passed into a block. Keys are
types, values are functions to that return a shape tuple
"""
# NOTE: figure out how to update this in the plugin system
# install imagepypelines_tensorflow
# e.g. DEFAULT_SHAPE_FUNCS.update({tf.Tensor : shape_fn})


# homogenus containers are containers like numpy arrays where every datum (row)
# is the same type and shape. We can speed up type and shape checking by
# only checking the first row
DEFAULT_HOMOGENUS_CONTAINERS = [np.ndarray]
"""default homogenus containers in ImagePypelines core. A list of data
containers that are "homogenus", meaning that every datum (row) will have the
same shape and type. By default, [numpy.ndarray]
"""

HOMOGENUS_CONTAINERS = DEFAULT_HOMOGENUS_CONTAINERS.copy()
"""a list of data containers that are "homogenus", meaning that every datum (row)
will have the same shape and type. By default, [numpy.ndarray]
"""
