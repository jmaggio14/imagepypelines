#
# @Email:  jmaggio14@gmail.com
#
# MIT License: https://github.com/jmaggio14/imsciutils/blob/master/LICENSE
#
# Copyright (c) 2018 Jeff Maggio, Nathan Dileas, Ryan Hartzell
#
import imsciutils
import numpy as np
from PIL import Image
from .coordinates import dimensions
from .. import util

def normalize_and_bin(src, max_count=255, cast_type=np.uint8):
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
    util.dtype_type_check(cast_type)

    img = src.astype(np.float32)
    img = (img / img.max()) * max_count
    img = img.astype(cast_type)
    return img


def quick_image_view(img, normalize_and_bin=False, title="quick view image"):
    """
    quickly displays the image using a PIL Image Viewer
    (which uses ImageMagick over X11 -- this will work over ssh)

    Args:
        img (np.ndarray): input image you want to view
        normalize_and_bin (bool, optional): Defaults to False
            boolean value indicating whether or not to normalize
            and bin the image
        title (str, optional): title for the image window.
            Default is 'quick view image'

    Returns:
        None
    """
    assert isinstance(img, np.ndarray), "'img' must be a np array or subclass"
    assert isinstance(normalize_and_bin, int), "'normalize_and_bin' must be int"
    assert isinstance(title, str), "'title' must be a string"

    if normalize_and_bin:
        img = globals()['normalize_and_bin'](img,
                                                max_count=255,
                                                cast_type=np.uint8)

    if len(img.shape) > 2:
        img = np.flip(img, 2)

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
    r,c,b,_ = dimensions(img)
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
