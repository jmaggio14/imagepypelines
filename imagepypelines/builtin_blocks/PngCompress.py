# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018-2019 Jeff Maggio, Nathan Dileas, Ryan Hartzell
#
import cv2
from .. import SimpleBlock, RGB, GRAY, ArrayType



class PngCompress(SimpleBlock):
    def __init__(self):
        io_kernel = {RGB : ArrayType([None,1]),
                    GRAY : ArrayType([None,1]),}

        super().__init__(io_kernel)

    def process(self, datum):
        return cv2.imencode('.png', datum)[1]
