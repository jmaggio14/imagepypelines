#
# marvin (c) by Jeffrey Maggio, Hunter Mellema, Joseph Bartelmo
#
# marvin is licensed under a
# Creative Commons Attribution-ShareAlike 4.0 International License.
#
# You should have received a copy of the license along with this
# work. If not, see <http://creativecommons.org/licenses/by-sa/4.0/>.
#
#
import marvin
import cv2
from PIL import Image
import numpy as np

class ImageViewer(object):
    """
    Class to simplify displaying images using opencv windows. Also has
    functionality to resize images automatically if desired

    On some systems (or opencv builds), openCV requires a waitkey to be
    called before displaying the image. This functionality is built in
    the view function with the argument 'force_waitkey'
    """
    def __init__(self,window_name,size=None,interpolation=cv2.INTER_NEAREST):
        self.window_name = str(window_name)
        self.size = size
        self.interpolation = interpolation
        self.open()

    def open(self):
        """
        opens the image viewer, automatically called in __init__
        input::
            None
        return::
            None
        """
        cv2.namedWindow(self.window_name)

    def view(self,frame,force_waitkey=True):
        """
        displays the frame passed into it, reopens itself if it
        input::
            frame (np.ndarray): image to be displayed
        return::
            force_waitkey (int) = 1:
                if greater than zero, then call a waitkey for the
                duration of the time given. this is required on some
                systems to display the image properly.
        """
        assert isinstance(frame,np.ndarray)

        if isinstance(self.size,(tuple,list)):
            frame = cv2.resize(frame,
                                    dsize=(self.size[1],self.size[0]),
                                    interpolation=self.interpolation)
        cv2.imshow(self.window_name,frame)
        if force_waitkey:
            cv2.waitKey( force_waitkey )

    def close(self):
        """
        closes the image viewing window
        input::
            None
        return::
            None
        """
        cv2.destroyWindow( self.window_name )

def normalize_and_bin(src,max_count=255,cast_type=np.uint8):
    """
    normalizes and bins the bins the input image to a given bit depth
    and max_count

    input::
        src (np.ndarray): input image
        max_count (int,float): max value in output image
        cast_type (numpy.dtype): np.dtype the final array is casted to

    return::
        img (np.ndarray): normalized and binned image

    """
    assert isinstance(src,np.ndarray),"'src' must be np.ndarray"
    assert isinstance(max_count,(int,float)),"'max_count' must be number"
    assert isinstance(cast_type,marvin.NUMPY_TYPES),\
                                    "'cast_type' must be a numpy number type"

    img = src.astype(np.float32)
    img = ( img / img.max() ) * max_count
    img = img.astype(cast_type)
    return img


def quick_image_view(img,normalize_and_bin=False,title="quick view image"):
    """
    quickly displays the image using a PIL Image Viewer

    input::
        img (np.ndarray):
            input image you want to view
        normalize_and_bin (bool) = False:
            boolean value indicating whether or not to normalize
            and bin the image

    return::
        None
    """
    assert isinstance(img,np.ndarray),"'img' must be a np array or subclass"
    assert isinstance(normalize_and_bin,int),"'normalize_and_bin' must be int"
    assert isinstance(title,str),"'title' must be a string"

    if normalize_and_bin:
        img = normalize_and_bin(img,max_count=255,cast_type=np.uint8)

    if len(img.shape) > 2:
        img = np.flip(img,2)

    img = Image.fromarray( img )
    img.show(title)
