# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018-2019 Jeff Maggio, Nathan Dileas, Ryan Hartzell
import os
import glob
import sys
from types import FunctionType

# JM: replaced SimpleNamespace import with this for python2 compatability
SimpleNamespace = type('SimpleNamespace', (object,), {})

from .imports import import_opencv
cv2 = import_opencv()
import numpy as np
from functools import partial
import pkg_resources


def list_standard_images():
    """returns a list of all builtin standard images sorted alphabetically"""
    return sorted(STANDARD_IMAGES.keys())

def standard_image_filenames():
    """returns a list of standard image filenames on the local machine"""
    sorted_keys = list_standard_images()
    filenames = [STANDARD_IMAGES[k] for k in sorted_keys]
    return filenames

def standard_image_gen():
    """
    generator function to yield all standard images sequentially
    useful for testing
    """
    for img_name in list_standard_images():
        yield get_standard_image(img_name)

def standard_images():
    """returns a list of all standard image arrays"""
    return list( standard_image_gen() )


def get_standard_image(img_name):
    """ retrieves the numpy array of standard image given a string key

    Args:
        img_name (str): name of the standard image to retrieve, must be in
            list_standard_images()

    Returns:
        np.ndarray: image data for the given standard image

    Raises:
        ValueError: if invalid img_name is provided

    Example:
        >>> lenna = get_standard_image('lenna')
    """
    if img_name in STANDARD_IMAGES:
        img = cv2.imread(STANDARD_IMAGES[img_name], cv2.IMREAD_UNCHANGED)
        if isinstance(img, type(None)):
            error_msg = "unable to find {name} at {path}".format(name=img_name,
                                                                 path=STANDARD_IMAGES[img_name])
            raise FileNotFoundError(error_msg)

        return img

    else:
        raise ValueError("unknown standard image key {img_name}, must be \
                            one of {std_imgs}".format(
            img_name=img_name,
            std_imgs=list_standard_images()))


# uses the pkg_resources provider to load in data in the .egg file
from .. import STANDARD_IMAGE_DIRECTORY
# ND 9/7/18 - dynamically populate paths to the standard test images
# assumes the only thing in the STANDARD_IMAGE_DIRECTORY are images
STANDARD_IMAGE_PATHS = list(
    glob.glob(os.path.join(STANDARD_IMAGE_DIRECTORY, '*')))
STANDARD_IMAGES = {os.path.basename(impath).split(
    '.')[0]: impath for impath in STANDARD_IMAGE_PATHS}

# ND 9/7/18 - create convenience functions to load each of the standard test
# images as attributes of func
funcs = SimpleNamespace()
for img_name in STANDARD_IMAGES.keys():
    # JM: modifies function creation to also include docstrings
    partial_func = partial(get_standard_image, img_name)
    # ND changed partial funcs to FunctionType
    std_img_func = FunctionType(
        partial_func.func.__code__, globals(), img_name, partial_func.args)

    std_img_func.__doc__ = "standard image retrieval for {}".format(img_name)
    globals()[img_name] = std_img_func
    setattr(funcs, img_name, std_img_func)

# JM: deletes last remaining partial function from scope to remove Sphinx warning
del partial_func


if __name__ == "__main__":
    main()
