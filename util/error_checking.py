"""
Helper functions that contain canned tests or checks that we will run
frequently
"""
import numpy as np
import imsciutils



def interpolation_type_check(interp):
    """
    checks to see if the interpolation type is one of the acceptable
    values specified in opencv, otherwise raises an
    imsciutils.InvalidInterpolationType error
    """
    if interp not in imsciutils.CV2_INTERPOLATION_TYPES:
        raise imsciutils.InvalidInterpolationType(interp)

    return True


def dtype_type_check(dtype):
    """
    checks to see if the interpolation type is one of the acceptable
    values specified in opencv, otherwise raises an
    imsciutils.InvalidInterpolationType error
    """
    if dtype not in imsciutils.NUMPY_TYPES:
        raise imsciutils.InvalidNumpyType(interp)

    return True


def is_numpy_array(arr):
    """returns True if input is a numpy array or subclass of numpy array"""
    return isinstance(arr,np.ndarray)
