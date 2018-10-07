from .. import SimpleBlock
import cv2

class Color2Gray(SimpleBlock):
    def __init__(self,
                    order='rgb',
                    name=None):

        if order == 'rgb':
            self.flag = cv2.COLOR_RGB2GRAY
        elif order == 'bgr':
            self.flag = cv2.COLOR_BGR2GRAY
        else:
            raise ValueError("unknown channel order, must be 'rgb' or 'bgr'")

        input_shape = [None,None,3]
        output_shape = [None,None]

        super(Resizer,self).__init__(input_shape=input_shape,
                                            output_shape=output_shape,
                                            name=name,
                                            requires_training=False)
    def process(self,datum):
        gray = cv2.cvtColor(datum, self.flag)
        return gray
