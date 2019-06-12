# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018-2019 Jeff Maggio, Nathan Dileas, Ryan Hartzell
#
from .. import SimpleBlock, ArrayIn, ArrayOut
from ..core import import_opencv
cv2 = import_opencv()
import numpy as np



class Otsu(SimpleBlock):
    def __init__(self,min=0,max=255):
        self.min = min
        self.max = max

        io_kernel = [
                    [ArrayIn(['M','M']),
                        ArrayOut(['N','M']),
                        "Threshold an input grayscale image using Otsu's method",]
                    ]
        super(Otsu,self).__init__(io_kernel,
                                    requires_training=False)

    def process(self,datum):
        _, otsu = cv2.threshold(datum.astype(np.uint8),
                                    self.min,
                                    self.max,
                                    cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        return otsu
