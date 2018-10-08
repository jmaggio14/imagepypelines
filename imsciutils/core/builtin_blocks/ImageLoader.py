# @Email:  jmaggio14@gmail.com
#
# MIT License: https://github.com/jmaggio14/imsciutils/blob/master/LICENSE
#
# Copyright (c) 2018 Jeff Maggio, Nathan Dileas, Ryan Hartzell
#
from .. import SimpleBlock
import cv2


class ImageLoader(SimpleBlock):
    """Block to load in imagery from filenames
    Reads in an image using an input filename

    Args:
        None
    """
    def __init__(self):
        input_shape = str
        output_shape = [None,None], [None,None,3]
        super(ImageLoader,self).__init__(input_shape=input_shape,
                                            output_shape=output_shape,
                                            requires_training=False)

    def process(self,datum):
        """loads in an image from a filename

        Args:
            datum (string): image filename

        Returns:
            image (np.ndarray): 2D or 3D array of image data
        """
        image = cv2.imread(datum)

        # throws error if unable to read image
        if image is None:
            error_msg = "unable to load {}".format(datum)
            self.printer.error(error_msg)
            raise FileNotFoundError(error_msg)

        return img
