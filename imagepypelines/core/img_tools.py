# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018-2020 Jeff Maggio, Nathan Dileas, Ryan Hartzell
import numpy as np
from PIL import Image
from .util import dtype_type_check, interpolation_type_check
from .imports import import_opencv
cv2 = import_opencv()

################################################################################
#                                   Functions
################################################################################


def display_safe(src, max_count=255, cast_type=np.uint8):
    """normalizes and bins an image

    normalizes and bins the bins the input image to a given bit depth
    and max_count

    Args:
        src (np.ndarray): input image
        max_count (int,float): max value in output image
        cast_type (numpy.dtype): np.dtype the final array is casted to

    Returns:
        np.ndarray: normalized and binned image

    """
    assert isinstance(src, np.ndarray), "'src' must be np.ndarray"
    assert isinstance(max_count, (int, float)), "'max_count' must be number"
    dtype_type_check(cast_type)

    img = norm_ab(src, 0, max_count).astype(cast_type)
    return img


def quick_image_view(img, display_safe=False, title="quick view image"):
    """
    quickly displays the image using a PIL Image Viewer
    (which uses ImageMagick over X11 -- this will work over ssh)

    Args:
        img (np.ndarray): input image you want to view
        display_safe (bool, optional): Defaults to False
            boolean value indicating whether or not to normalize
            and bin the image
        title (str, optional): title for the image window.
            Default is 'quick view image'

    Returns:
        None
    """
    assert isinstance(img, np.ndarray), "'img' must be a np array or subclass"
    assert isinstance(display_safe, int), "'display_safe' must be int"
    assert isinstance(title, str), "'title' must be a string"

    if display_safe:
        img = norm_ab(img, 0, 255)

    if len(img.shape) > 2:
        img = np.flip(img, 2)

    img = img.astype(np.uint8)
    img = Image.fromarray(img)
    img.show(title)


def number_image(img, num):
    """Adds a number to the corner of an image

    Args:
        img (np.ndarray): image
        num (int,str): number to put in the corner of the image

    Returns:
        np.ndarray: numbered image
    """
    r,c,b = dimensions(img)
    loc = int( min(r,c) * .95 )
    color = (255,255,255)
    if np.mean(img[int(.9*r):r,int(.9*c):c]) > 128:
        color = (0,0,0)

    img = cv2.putText(img,
                        text=str(num),
                        org=(loc,loc),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=.5,
                        color=color,
                        thickness=2,
                        bottomLeftOrigin=False)

    return img

def centroid(img):
    """finds the centroid of the given image img

    Args:
        img (np.ndarray):
            input img to find the centroid of
    Returns:
        tuple: centroid of the input image (height,width)

    Example:
        >>> import imagepypelines as ip
        >>> lenna_centroid = ip.centroid( ip.lenna() )
    """
    assert isinstance(img, np.ndarray), "'img' must be a np array or subclass"

    centroid = img.shape[0]//2, img.shape[1]//2
    return centroid


def frame_size(img):
    """return the height and width of a given img

    Args:
        img (np.ndarray): input img to find frame_size of

    Returns:
        tuple: frame_size, height and width of the input img

    Example:
        >>> import imagepypelines as ip
        >>> height, width = ip.frame_size( ip.lenna() )
    """
    assert isinstance(img, np.ndarray), "'img' must be a np array or subclass"

    frame_size = img.shape[0], img.shape[1]
    return frame_size


def dimensions(img):
    """
    function which returns the dimensions and data_type of a given image

    Args:
        img (np.ndarray): input image

    Returns:
        tuple: dimensions of the form (rows, cols, bands)

    Example:
        >>> import imagepypelines as ip
        >>> rows, cols, bands = ip.dimensions( ip.lenna() )
    """
    assert isinstance(img, np.ndarray), "'img' must be a np array or subclass"

    rows = img.shape[0]
    cols = img.shape[1]
    if img.ndim == 3:
        bands = img.shape[2]
    else:
        bands = 1

    return (rows, cols, bands)

def norm_01(img):
    """ Normalize img to the range [0, 1], inclusive.

    Args:
        img (np.ndarray): image to normalize, can be any dtype.

    Returns:
        np.ndarray: normalized image, dtype=np.float64
    """
    assert isinstance(img, np.ndarray), "'img' must be a np array or subclass"

    img_out = img.astype(np.float64)
    img_out = (img_out - img_out.min()) / (img_out.max() - img_out.min())

    return img_out


def norm_ab(img, a, b):
    """ Normalize img to the range [a, b], inclusive. Float output by default.

    If a < b, then the histogram will just be scaled and shifted.
    If b > a, then the histogram will be flipped left-right, scaled, and shifted.

    Args:
        img (np.ndarray): image to normalize, can be any dtype.
        a (float): one end of range
        b (float): other end of range

    Returns:
        np.ndarray: normalized image, dtype=np.float64
    """
    img_out = norm_01(img)
    # scale to the extent of the range, then shift to match
    img_out = (img_out * (b - a)) + a

    return img_out


def norm_dtype(img, dtype=np.uint8):
    """ Normalize img to the range [dtype_min, dtype_max].

    Can be used to prepare images for file output.
    Equivalent to a 0% histogram stretch.
    Works by converting to float64, then stretching/shifting, then quantizing.

    Args:
        img (np.ndarray): image to normalize, can be any dtype.
        dtype (np dtype): integer datatype to normalize to.

    Returns:
        np.ndarray: normalized image, dtype=dtype
    """
    assert isinstance(img, np.ndarray), "'img' must be a np array or subclass"

    dtype_info = np.iinfo(dtype)

    return norm_ab(img, dtype_info.min, dtype_info.max).astype(dtype)



def low_pass(img,cut_off,filter_type='ideal',butterworth_order=1):
    """calculates a lowpass filter for an input image

    Args:
        img(np.ndarray): image to calculate filter for
        cut_off (float): cutoff frequency for this filter. units in #TODO
        filter_type (str): the type of filter to apply, 'ideal','gaussian',
            'butterworth'
        butterworth_order(float): butterworth order if butterworth filter is
            being used

    Returns:
        filter(np.ndarray) 2D filter
    """
    r,c,b = dimensions(img)
    u = np.arange(r)
    v = np.arange(c)
    u, v = np.meshgrid(u, v)
    low_pass = np.sqrt( (u-r/2)**2 + (v-c/2)**2 )

    if filter_type == 'ideal':
        low_pass[low_pass <= cut_off] = 1
        low_pass[low_pass >= cut_off] = 0

    elif filter_type == 'gaussian':
        xp = -1*(low_pass**2) / (2* cut_off**2)
        low_pass = np.exp( xp )
        low_pass = np.clip(low_pass,0,1)

    elif filter_type == 'butterworth':
        denom = 1.0 + (low_pass / cut_off)**(2 * order)
        low_pass = 1.0 / denom


    return low_pass



def high_pass(img,cut_off,filter_type='ideal',butterworth_order=1):
    """calculates a highpass filter for an input image

    Args:
        img(np.ndarray): image to calculate filter for
        cut_off (float): cutoff frequency for this filter. units in #TODO
        filter_type (str): the type of filter to apply, 'ideal','gaussian',
            'butterworth'
        butterworth_order(float): butterworth order if butterworth filter is
            being used

    Returns:
        filter(np.ndarray) 2D filter
    """
    return 1 - low_pass(img,cut_off,filter_type='ideal',butterworth_order=1)

################################################################################
#                                   Classes
################################################################################


class Viewer(object):
    """
    Class to simplify displaying images using opencv windows. Also has
    functionality to resize images automatically if desired

    On some systems (or opencv builds), openCV requires a waitkey to be
    called before displaying the image. This functionality is built in
    the view function with the argument 'force_waitkey'


    Args:
        window_name (str): the name of the window
        size (2 element tuple, None): (height, width) to resize image to
        interpolation (cv2 constant): cv2 interpolation flag for resizing
        enable_frame_counter (bool): whether or not to enable frame counter

    Attributes:
        window_name: name of the cv2 window
        size: size the images are being resized to
        interpolation: type of interpolation being usef for resizing
        enable_frame_counter: whether or not the frame counter is enabled
        frame_counter: index of the frame currently displayed

    """

    def __init__(self,
                 window_name=None,
                 size=None,
                 FFT=False,
                 normalize=False,
                 interpolation=cv2.INTER_NEAREST,
                 enable_frame_counter=False):

        interpolation_type_check(interpolation)
        if window_name is None:
            window_name = datetime.now()

        self.window_name = str(window_name)
        self.size = size
        self._FFT = FFT
        self._normalize = normalize
        self.interpolation = interpolation
        self._enable_frame_counter = enable_frame_counter
        self.open()
        self.frame_counter = 1

    def open(self):
        """
        opens the image viewer, automatically called in __init__

        Args:
            None

        Returns:
            None
        """
        cv2.namedWindow(self.window_name, cv2.WINDOW_AUTOSIZE)
        return self

    def view(self, frame, force_waitkey=True):
        """
        displays the frame passed into it, reopens itself if it

        Args:
            frame (np.ndarray): image to be displayed

        Returns:
            force_waitkey (int) = 1:
                if greater than zero, then call a waitkey for the
                duration of the time given. this is required on some
                systems to display the image properly.
        """
        assert isinstance(frame, np.ndarray), "'frame' must be a numpy array"
        assert frame.ndim in [2, 3], "'frame' must be a 2D or 3D array"
        assert isinstance(force_waitkey, (int, float)),\
            "'force_waitkey' must be an integer"

        # normalize image band by band (useful for FFT viewing)
        if self._FFT:

            if frame.ndim == 2:

                frame = 20*np.log(np.abs(frame))

            if frame.ndim == 3:

                for b in range(0, 3):

                    frame[:,:,b] = 20*np.log(np.abs(frame[:,:,b]))

        if self._normalize:

            frame = norm_dtype(frame)

        # cast frame dtype to uint8 for display
        frame = frame.astype(np.uint8)

        if isinstance(self.size, (tuple, list)):
            frame = cv2.resize(frame,
                               dsize=(self.size[1], self.size[0]),
                               interpolation=self.interpolation)

        # add a frame counter to an image thin
        if self._enable_frame_counter:
            frame = number_image(frame,self.frame_counter)

        # displaying the image
        cv2.imshow(self.window_name, frame)

        if force_waitkey:
            cv2.waitKey(force_waitkey)

        self.frame_counter += 1

    def enable_frame_counter(self):
        """enable the frame counter"""
        self._enable_frame_counter = True

    def disable_frame_counter(self):
        """disable the frame counter"""
        self._enable_frame_counter = False

    def close(self):
        """
        closes the image viewing window

        Args:
            None

        Returns:
            None
        """
        cv2.destroyWindow(self.window_name)
        return self

    def __del__(self):
        self.close()
