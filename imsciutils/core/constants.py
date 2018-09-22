import numpy as np
import cv2
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
"""module variable which contains all image extensions openable by opencv"""
