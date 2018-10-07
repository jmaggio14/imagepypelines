from .. import SimpleBlock
import cv2

class Resizer(SimpleBlock):
    def __init__(self,
                    to_height=512,
                    to_width=512,
                    interpolation=cv2.INTER_NEAREST):
        self.to_height = to_height
        self.to_width = to_width
        self.interpolation

        input_shape = [None,None], [None,None,3]
        output_shape = [None,None], [None,None,3]

        super(Resizer,self).__init__(input_shape=input_shape,
                                            output_shape=output_shape,
                                            requires_training=False)
    def process(self,datum):
        resize = cv2.resize(datum,
                       dsize=(self.to_width,self.to_height),
                       interpolation=self.interpolation)
        return resized
