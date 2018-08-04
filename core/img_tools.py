import imgscitools
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
    assert isinstance(cast_type, imscitools.NUMPY_TYPES),\
        "'cast_type' must be a numpy number type"

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
        img = normalize_and_bin(img, max_count=255, cast_type=np.uint8)

    if len(img.shape) > 2:
        img = np.flip(img, 2)

    img = Image.fromarray(img)
    img.show(title)
