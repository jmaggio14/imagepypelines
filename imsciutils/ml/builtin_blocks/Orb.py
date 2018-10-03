from .. import BaseBlock
from ... import core
# from .. import ..core as core
import cv2
import numpy as np

class Orb(BaseBlock):
    def setup(self,n_keypoints=100):
        assert isinstance(n_keypoints,(int,float)),"'n_keypoints' must be int"
        self.n_keypoints = n_keypoints
        self.orb = cv2.ORB_create(self.n_keypoints)
        return self

    def validate_data(self,x_data):
        """makes sure the input data is the correct type

        validates that 'x_data' is a numpy array of shape (n_img,height,width,bands)
        """
        assert isinstance(x_data,np.ndarray),"'x_data' must be a 4D np.ndarray"
        assert x_data.ndim == 4,"'x_data' must be a 4D np.ndarray"
        assert x_data.shape[-1] == 1,"'x_data' must be a grayscale"

    def process(self,x_data):
        """calculates descriptors on a 4D img_stack (n_img,height,width,bands)

        If there are not enough keypoints calculated to populate the output
        array, the descriptor vectors will be replaced with zeros

        Args:
            x_data (np.ndarray): 4D numpy array to process
                (n_img,height,width,bands)

        Returns:
            descriptors(np.ndarray): 3D array of ORB descriptors
                (n_imgs,n_keypoints,32)

        """
        # JM: storage array for all image descriptors
        # (n_images,n_keypoints,32)
        descriptors = np.zeros( (x_data.shape[0],self.n_keypoints,32) )
        for i in range(x_data.shape[0]):
            img = x_data[i,:,:,:].reshape((x_data.shape[1],x_data.shape[2]))
            img = np.uint8(img)
            _,des = self.orb.detectAndCompute(img,None)
            if des is None:
                #JM: for edge case where no descriptors are found
                continue
            descriptors[i,0:des.shape[0],:] = des

        return descriptors
