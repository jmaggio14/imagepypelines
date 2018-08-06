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

CV2_INTERPOLATION_TYPES = (cv2.INTER_NEAREST,
                           cv2.INTER_LINEAR,
                           cv2.INTER_AREA,
                           cv2.INTER_CUBIC,
                           cv2.INTER_LANCZOS4,)
