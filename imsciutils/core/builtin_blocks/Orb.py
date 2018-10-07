#
# @Email:  jmaggio14@gmail.com
#
# MIT License: https://github.com/jmaggio14/imsciutils/blob/master/LICENSE
#
# Copyright (c) 2018 Jeff Maggio, Nathan Dileas, Ryan Hartzell
#
from .. import SimpleBlock
import cv2
import numpy as np

class Orb(SimpleBlock):
    def setup(self,n_keypoints=100):
        if not isinstance(n_keypoints,(int,float)):
            error_msg = "'n_keypoints' must be int"
            self.printer.error(error_msg)
            raise TypeError(error_msg)

        self.n_keypoints = int(n_keypoints)
        self.orb = cv2.ORB_create(self.n_keypoints)

    def process(self,datum):
        """calculates descriptors on a 4D img_stack (n_img,height,width,bands)

        If there are not enough keypoints calculated to populate the output
        array, the descriptor vectors will be replaced with zeros

        Args:
            datum (np.ndarray): image numpy array to process
                shape = (width,bands)

        Returns:
            descriptors(np.ndarray): 2D array of ORB descriptors
                shape = (n_keypoints,32)

        """
        _,des = self.orb.detectAndCompute(img,None)
        return des
