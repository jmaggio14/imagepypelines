import imsciutils
import numpy as np
from PIL import Image


def normalize_and_bin(src, max_count=255, cast_type=np.uint8):
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
    assert isinstance(src, np.ndarray), "'src' must be np.ndarray"
    assert isinstance(max_count, (int, float)), "'max_count' must be number"
    iu.util.dtype_type_check(cast_type)

    img = src.astype(np.float32)
    img = (img / img.max()) * max_count
    img = img.astype(cast_type)
    return img


def quick_image_view(img, normalize_and_bin=False, title="quick view image"):
    """
    quickly displays the image using a PIL Image Viewer
    (which uses ImageMagick -- this will work over ssh)

    input::
        img (np.ndarray):
            input image you want to view
        normalize_and_bin (bool) = False:
            boolean value indicating whether or not to normalize
            and bin the image

    return::
        None
    """
    assert isinstance(img, np.ndarray), "'img' must be a np array or subclass"
    assert isinstance(normalize_and_bin, int), "'normalize_and_bin' must be int"
    assert isinstance(title, str), "'title' must be a string"

    if normalize_and_bin:
        img = iu.normalize_and_bin(img, max_count=255, cast_type=np.uint8)

    if len(img.shape) > 2:
        img = np.flip(img, 2)

    img = Image.fromarray(img)
    img.show(title)


def number_image(img,num):
    """
    Adds a number to the corner of an image

    input::
        img (np.ndarray): image
        num (int): number to put in the corner of the image

    returns::
        img (np.ndarray): numbered image
    """
    r,c,b,_ = iu.dimensions(img)
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

    img
