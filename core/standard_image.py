import os
import cv2
import numpy as np

IMAGE_SRC_DIRECTORY = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'data')
STANDARD_IMAGES = {'lenna': os.path.join(IMAGE_SRC_DIRECTORY, 'lenna.tif'),
                   'lenna_gray': os.path.join(IMAGE_SRC_DIRECTORY, 'lenna_gray.tif'),
                   'crowd': os.path.join(IMAGE_SRC_DIRECTORY, 'crowd.jpg'),
                   'redhat': os.path.join(IMAGE_SRC_DIRECTORY, 'redhat.ppm'),
                   'panda': os.path.join(IMAGE_SRC_DIRECTORY, 'panda.jpg'),
                   'linear': os.path.join(IMAGE_SRC_DIRECTORY, 'linear.tif'),
                   'panda_color': os.path.join(IMAGE_SRC_DIRECTORY, 'panda_color.jpg'),
                   'gecko': os.path.join(IMAGE_SRC_DIRECTORY, 'gecko.jpg'),
                   # 'checkerboard': os.path.join(IMAGE_SRC_DIRECTORY, 'checkerboard.tif'),
                   'sparse_checkerboard': os.path.join(IMAGE_SRC_DIRECTORY, 'sparse_checkerboard.tif'),
                   'roger': os.path.join(IMAGE_SRC_DIRECTORY, 'roger.jpg'),
                   'pig': os.path.join(IMAGE_SRC_DIRECTORY, 'pig.jpg'),
                   'carlenna': os.path.join(IMAGE_SRC_DIRECTORY, 'carlenna.png',)
                   }

def list_standard_images():
    """returns a list of all builtin standard images sorted alphabetically"""
    return sorted( list(STANDARD_IMAGES.keys()) )


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

    e.g.
        import numpy as np
        import cv2

        @standard_image_input
        def add_one_to_image(img):
            assert isinstance(img,np.ndarray) #forcing a np.ndarray input type
            return img + 1

        lenna_plus_one = add_one_to_image('lenna')
        #these are now equivalent
        lenna_plus_one = add_one_to_image( cv2.imread('lenna.jpg') )

    """
    def _standard_image_input(img, *args, **kwargs):
        if not isinstance(img,np.ndarray):
            # must check if img is numpy array first, because numpy
            # arrays are not hashable
            if img in STANDARD_IMAGES:
                img = get_standard_image(img)

        ret = func(img, *args, **kwargs)
        return ret
    return _standard_image_input


def get_standard_image(img_name):
    """
    retrieves the numpy array of standard image given a string key

    input::
        img_name (str):
                name of the standard image to retrieve, must be in
                list_standard_images()

    return::
        img (np.ndarray): image data for the given standard image

    raises::
        ValueError if invalid img_name is provided

    example::
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


def lenna():
    """retrieves image data for 'lenna' reference image"""
    return get_standard_image('lenna')


def lenna_gray():
    """retrieves image data for 'lenna_gray' reference image"""
    return get_standard_image('lenna_gray')


def crowd():
    """retrieves image data for 'crowd' reference image"""
    return get_standard_image('crowd')


def redhat():
    """retrieves image data for 'redhat' reference image"""
    return get_standard_image('redhat')


def linear():
    """retrieves image data for 'linear' reference image"""
    return get_standard_image('linear')


def panda():
    """retrieves image data for 'panda' reference image"""
    return get_standard_image('panda')


def panda_color():
    """retrieves image data for 'panda_color' reference image"""
    return get_standard_image('panda_color')


def gecko():
    """retrieves image data for 'gecko' reference image"""
    return get_standard_image('gecko')

# TODO - add source file to repo and uncomment this function
# def checkerboard():
#     """retrieves image data for 'checkerboard' reference image"""
#     return get_standard_image('checkerboard')


def sparse_checkerboard():
    """retrieves image data for 'sparse_checkerboard' reference image"""
    return get_standard_image('sparse_checkerboard')


def roger():
    """retrieves image data for 'roger' reference image"""
    return get_standard_image('roger')


def pig():
    """retrieves image data for 'pig' reference image"""
    return get_standard_image('pig')


def carlenna():
    """retrieves image data for 'carlenna' reference image"""
    return get_standard_image('carlenna')


def main():
    """tests functionality by loading and printing out every image"""
    for img in STANDARD_IMAGES:
        print(get_standard_image(img))


if __name__ == "__main__":
    main()
