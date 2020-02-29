# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018-2020 Jeff Maggio, Nathan Dileas, Ryan Hartzell
import numpy as np
from .imports import import_opencv
cv2 = import_opencv()

# MODIFY THIS VARIABLE EVERY TIME A NEW IMPORTABLE CONSTANT IS ADDED
# You must also modify the unit test 'test_constants' located in test_core.py
__all__ = ['NUMPY_TYPES',
            'CV2_INTERPOLATION_TYPES',
            'IMAGE_EXTENSIONS',
            'PRETRAINED_NETWORKS',
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

CV2_INTERPOLATION_TYPES = (cv2.INTER_NEAREST,
                           cv2.INTER_LINEAR,
                           cv2.INTER_AREA,
                           cv2.INTER_CUBIC,
                           cv2.INTER_LANCZOS4,)
"""module variable which contains all opencv interpolation variables"""




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


PRETRAINED_NETWORKS = [
                    'xception',
                    'vgg16',
                    'vgg19',
                    'resnet50',
                    'inception_v3',
                    'inception_resnet_v2',
                    'mobilenet',
                    'densenet121',
                    'densenet169',
                    'densenet201',
                    ]
"""module variable which contains all usable pretrained network names for the
        PretrainedNetwork block
"""
