# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018 Jeff Maggio, Nathan Dileas, Ryan Hartzell
#
from .BaseBlock import ArrayType


class GrayscaleImage(ArrayType):
    """convienence wrapper to create an io_map ArrayType for Grayscale imagery"""
    def __init__(self):
        super(GrayscaleImage,self).__init__([None,None])

class RgbImage(ArrayType):
    """convienence wrapper to create an io_map ArrayType for Rgb imagery"""
    def __init__(self):
        super(RgbImage,self).__init__([None,None,3])

RGB = RgbImage()
GRAY = GrayscaleImage()
