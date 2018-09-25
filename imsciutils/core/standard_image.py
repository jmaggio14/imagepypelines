#
# @Email:  jmaggio14@gmail.com
#
# MIT License
#
# Copyright (c) 2018 Jeff Maggio, Nathan Dileas, Ryan Hartzell
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
import os
import glob
import sys
from types import SimpleNamespace

import cv2
import numpy as np
from functools import partial
import pkg_resources


def list_standard_images():
    """returns a list of all builtin standard images sorted alphabetically"""
    return sorted(list(STANDARD_IMAGES.keys()))


def standard_image_gen():
    """
    generator function to yield all standard images sequentially
    useful for testing
    """
    for img_name in list_standard_images():
        yield get_standard_image(img_name)


def standard_image_input(func):
    """
    decorator which will parse a function inputs and retrieve a standard
    test image to feed into the function

    This decorator assumes that the first argument it's wrapped function
    is meant to be a numpy array image.

    Example:
        import numpy as np
        import cv2

        @standard_image_input
        def add_one_to_image(img):
            assert isinstance(img,np.ndarray) #forcing a np.ndarray input type
            return img + 1

        lenna_plus_one = add_one_to_image('lenna')
        # these are now equivalent
        lenna_plus_one = add_one_to_image( cv2.imread('lenna.jpg') )

    """
    def _standard_image_input(img, *args, **kwargs):
        if not isinstance(img, np.ndarray):
            # must check if img is numpy array first, because numpy
            # arrays are not hashable
            if img in STANDARD_IMAGES:
                img = get_standard_image(img)

        ret = func(img, *args, **kwargs)
        return ret
    return _standard_image_input


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
        lenna_data = get_standard_image('lenna')
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
# STANDARD_IMAGE_DIRECTORY = os.path.abspath(
#     os.path.join(
#         os.path.abspath(os.path.dirname(__file__)),
#         '..',
#         'data',
#         'standard_images'))
STANDARD_IMAGE_PATHS = list(glob.glob(os.path.join(STANDARD_IMAGE_DIRECTORY, '*')))
STANDARD_IMAGES = {os.path.basename(impath).split(
    '.')[0]: impath for impath in STANDARD_IMAGE_PATHS}

# ND 9/7/18 - create convenience functions to load each of the standard test
# images as attributes of func
funcs = SimpleNamespace()
for img_name in STANDARD_IMAGES.keys():
    setattr(funcs, img_name, partial(get_standard_image, img_name))



def main():
    """tests functionality by loading and printing out every image"""

    # ND 9/7/18 - FIXME:, this func should be a separate test file
    # Since it's here I'll add a line showing how my functonality can be used.

    for img in STANDARD_IMAGES:
        print(get_standard_image(img))

    print(funcs.lenna())
    print(funcs.roger())


if __name__ == "__main__":
    main()
