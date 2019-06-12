# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018-2019 Jeff Maggio, Nathan Dileas, Ryan Hartzell
#
import cv2
from .. import SimpleBlock, ArrayIn, ArrayOut



class PngCompress(SimpleBlock):
    def __init__(self):
        io_kernel = [
                        [ArrayIn(['N','M',3]),
                            ArrayOut(['N',1]),
                            "Compress color image to a png vector"],
                        [ArrayIn(['N','M']),
                            ArrayOut(['N',1]),
                            "Compress grayscale image to a png vector"]
                    ]
        super().__init__(io_kernel)

    def process(self, datum):
        return cv2.imencode('.png', datum)[1]
