from .BaseBlock import ArrayType


class GrayscaleImage(ArrayType):
    """convienence wrapper to create an io_map ArrayType for Grayscale imagery"""
    def __init__(self):
        super(GrayscaleImage,self).__init__([None,None])

class RgbImage(ArrayType):
    """convienence wrapper to create an io_map ArrayType for Rgb imagery"""
    def __init__(self):
        super(RgbImage,self).__init__([None,None,3])
