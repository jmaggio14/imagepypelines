from .. import SimpleBlock, ArrayType
import cv2



class Otsu(SimpleBlock):
    def __init__(self,min=0,max=255):
        self.min = min
        self.max = max

        io_map = {ArrayType([None,None]):ArrayType([None,None]),
                    ArrayType([None,None,3]):ArrayType([None,None,3])}
        super(Otsu,self).__init__(io_map,
                                    requires_training=False)

    def process(self,datum):
        _,otsu = cv2.threshold(datum,
                                self.min,
                                self.max,
                                cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        return otsu
