# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018 - 2020 Jeff Maggio, Jai Mehra, Ryan Hartzell
import numpy as np

# MODIFY THIS VARIABLE EVERY TIME A NEW IMPORTABLE CONSTANT IS ADDED
# You must also modify the unit test 'test_constants' located in test_core.py
__all__ = [
            'UUID_ORDER',
            'NUMPY_TYPES',
            'IMAGE_EXTENSIONS',
            ]


UUID_ORDER = 6
"""number of digits for pipeline and block UUIDS. default is 6 (~16.7million)"""


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

IMAGE_EXTENSIONS = ['png',
                    'jpg',
                    'tiff',
                    'tif',
                    'bmp',
                    'dib',
                    'jp2',
                    'jpe',
                    'jpeg',
                    'webp',
                    'pbm',
                    'pgm',
                    'ppm',
                    'sr',
                    'ras']
"""module variable which contains all image extensions openable by opencv's imread"""
