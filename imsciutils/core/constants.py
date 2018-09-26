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
import numpy as np
import cv2

# MODIFY THIS VARIABLE EVERY TIME A NEW IMPORTABLE CONSTANT IS ADDED
__all__ = ['NUMPY_TYPES',
            'CV2_INTERPOLATION_TYPES',
            'IMAGE_EXTENSIONS']


# ------------------Standard Type Tables------------------
NUMPY_TYPES = (np.uint8,
               np.int8,
               np.uint16,
               np.int16,
               np.int32,
               np.float32,
               np.float64,
               np.complex64,
               np.complex128)
"""module variable which contains all acceptable numpy dtypes"""

CV2_INTERPOLATION_TYPES = (cv2.INTER_NEAREST,
                           cv2.INTER_LINEAR,
                           cv2.INTER_AREA,
                           cv2.INTER_CUBIC,
                           cv2.INTER_LANCZOS4,)
"""module variable which contains all opencv interpolation variables"""




IMAGE_EXTENSIONS = ['.png',
                    '.jpg',
                    '.tiff',
                    '.tif',
                    '.bmp',
                    '.dib',
                    '.jp2',
                    '.jpe',
                    '.webp',
                    '.pbm',
                    '.pgm',
                    '.ppm',
                    '.sr',
                    '.ras']
"""module variable which contains all image extensions openable by opencv's imread"""
