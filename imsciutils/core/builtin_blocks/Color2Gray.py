from .. import SimpleBlock
from ..coordinates import dimensions
import cv2

class Color2Gray(SimpleBlock):
    """Block to convert color imagery to greyscale imagery

    Args:
        order(str): the channel order of the imagery, must be 'rgb' or 'bgr'
            default is 'rgb'
    """
    def __init__(self, order='rgb'):
        if order == 'rgb':
            self.flag = cv2.COLOR_RGB2GRAY
        elif order == 'bgr':
            self.flag = cv2.COLOR_BGR2GRAY
        else:
            raise ValueError("unknown channel order, must be 'rgb' or 'bgr'")

        input_shape = [None,None,3],[None,None]
        output_shape = [None,None]

        super(Resizer,self).__init__(input_shape=input_shape,
                                            output_shape=output_shape,
                                            requires_training=False)
    def process(self,datum):
        """converts color image to grayscale
        converts to grayscale, or does nothing if image is already grayscale

        Args:
            datum(np.ndarray): image to convert

        Returns:
            gray(np.ndarray): grayscale image
        """
        if datum.ndim == 2:
            # Image is already grayscale
            return datum

        gray = cv2.cvtColor(datum, self.flag)
        return gray
