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

# NOTE: figure out how to update this in the plugin system
# install imagepypelines_tensorflow
# {tf.Tensor : shape_fn}
