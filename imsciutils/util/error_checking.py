#
# @Email:  jmaggio14@gmail.com
#
# MIT License
#
# Copyright (c) 2018 Jeff Maggio, Nathan Dileas, Ryan Hartzell
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
"""
Helper functions that contain canned tests or checks that we will run
frequently
"""
import numpy as np
from collections import Iterable

from .. import core


def interpolation_type_check(interp):
    """
    checks to see if the interpolation type is one of the acceptable
    values specified in opencv, otherwise raises an
    imsciutils.InvalidInterpolationType error
    """
    if interp not in core.CV2_INTERPOLATION_TYPES:
        raise core.InvalidInterpolationType(interp)

    return True


def dtype_type_check(dtype):
    """
    checks to see if the interpolation type is one of the acceptable
    values specified in opencv, otherwise raises an
    imsciutils.InvalidInterpolationType error
    """
    if dtype not in core.NUMPY_TYPES:
        raise core.InvalidNumpyType(interp)

    return True


def is_numpy_array(arr):
    """returns True if input is a numpy array or subclass of numpy array"""
    return isinstance(arr,np.ndarray)

def is_iterable(var):
    """returns True if input is an iterable type, false otherwise"""
    return isinstance(var,Iterable)



def type_error_message(variable,variable_name,desired_types):
    """
    returns an error message for a type error_msg
    inputs:
        variable (the variable you want raise an error for):
        variable_name (the name of variable):
        desired_types (type,iterable of desired types):
    returns:
        error_msg (str): formatted error message string
    """
    if not isinstance(desired_types,Iterable):
        desired_types = [desired_types]
    error_msg =  "'{name}' must be on of [{desired}], currently is {cur}".format(name=variable_name,
                                                                                desired=','.join(desired_types),
                                                                                cur=type(variable))
    return error_msg
