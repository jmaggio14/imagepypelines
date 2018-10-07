# @Email:  jmaggio14@gmail.com
#
# MIT License: https://github.com/jmaggio14/imsciutils/blob/master/LICENSE
#
# Copyright (c) 2018 Jeff Maggio, Nathan Dileas, Ryan Hartzell
#
from .. import SimpleBlock
import cv2


class ImageLoader(SimpleBlock):
    def process(self,datum):
        """loads in an image from a filename

        Args:
            datum (string): image filename

        Returns:
            image (np.ndarray): 2D or 3D array of image data
        """
        image = cv2.imread(datum, cv2.IMREAD_UNCHANGED)

        # throws error if unable to read image
        if image is None:
            error_msg = "unable to load {}".format(datum)
            self.printer.error(error_msg)
            raise FileNotFoundError(error_msg)

        return img
