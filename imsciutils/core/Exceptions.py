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
from .printout import error as iuerror
import cv2

class CameraReadError(ValueError):
    """Exception raised when the CameraCapture device is unable to
    read the camera
    """
    pass

class InvalidInterpolationType(TypeError):
    """
    Exception for an invalid interpolation Type where it's applicable

    Args:
        interp (cv2.constant): interpolation type
    """
    def __init__(self,interp):
        interp_string = """cv2.INTER_NEAREST --> {}
                        cv2.INTER_LINEAR --> {}
                        cv2.INTER_AREA --> {}
                        cv2.INTER_CUBIC --> {}
                        cv2.INTER_LANCZOS4 --> {}""".format(cv2.INTER_NEAREST,
                                                            cv2.INTER_LINEAR,
                                                            cv2.INTER_AREA,
                                                            cv2.INTER_CUBIC,
                                                            cv2.INTER_LANCZOS4)
        error_string = "'interpolation' ({}) must be one of the following!"\
                                                            .format(interp)
        error_string = error_string + '\n' + interp_string
        iuerror(error_string)
        super(InvalidInterpolationType,self).__init__(error_string)


class InvalidNumpyType(TypeError):
    """
    Exception for an invalid interpolation Type where it's applicable

    Args:
        dtype (np.dtype): numpy datatype
    """
    def __init__(self,dtype):
        error_string = "'dtype' ({}) must be one of the following!"\
                                                            .format(dtype)
        error_string += "\n\t".join(iu.NUMPY_TYPES)
        iuerror(error_string)
        super(InvalidNumpyType,self).__init__(error_string)
