import cv2
from .. import SimpleBlock, RGB, GRAY, ArrayType



class PngCompress(SimpleBlock):
    def __init__(self):
        io_kernel = {RGB : ArrayType([None,1]),
                    GRAY : ArrayType([None,1]),}

        super().__init__(io_kernel)

    def process(self, datum):
        return cv2.imencode('.png', datum)[1]
