# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018-2020 Jeff Maggio, Ryan Hartzell, and collaborators
#
import os
import glob
import sys
from types import FunctionType, SimpleNamespace
import numpy as np
from functools import partial
import pkg_resources
import time
import smtplib
import getpass
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from cryptography import fernet
from uuid import uuid4
import base64

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from .imports import import_opencv
from .constants import IMAGE_EXTENSIONS
cv2 = import_opencv()



################################################################################
#                                   Constants
################################################################################



################################################################################
#                                   Functions
################################################################################

def passgen(passwd, salt=''):
    """generate a hashed key from a password

    Args:
        passwd (None,str): password to hash
        salt (str): optional, salt for your password

    Returns:
        bytes: hashed passkey safe string
    """
    # generate a proper key using Fernet library
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt.encode(),
        iterations=100000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode( kdf.derive( passwd.encode() ) )



# ------------------------------ Standard Imagery ------------------------------
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
        >>> import imagepypelines as ip
        >>> lenna = ip.get_standard_image('lenna')
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
from imagepypelines import STANDARD_IMAGE_DIRECTORY
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
del partial_func, img_name


# -------------------------------- Input/Output --------------------------------

def prevent_overwrite(filename,create_file=False):
    """
    checks to see if a file or directory already exists and creates a
    new filename if it does. It can also create the file if specificed

    when creating a file, this function assumes that if there is no file
    extension then it should create a directory

    NOTE:
        This function creates unique filenames by creating them and
        checking their current existence. THIS CAN BE A SLOW
        PROCESS -- it is much more efficient to keep track of filenames
        internally in your application

    Args:
        filename (str): the full file or directory path to be
            overwrite protected
        create_file (bool): Default is False
            boolean indicating whether or not to create the file
            before returning

    Returns:
        str: the assuredly unique output filename
    """
    base_filename,extension = os.path.splitext(filename)
    out_filename = filename
    file_exists = os.path.exists(out_filename)
    num = 1


    while file_exists:
        out_filename = "{base}({num}){ext}".format(base=base_filename,
                                        num=make_numbered_prefix(num,0),
                                        ext=extension)
        num += 1
        file_exists = os.path.exists(out_filename)

    if create_file:
        if extension == "":
            input_is_directory = True
        else:
            input_is_directory = False

        if input_is_directory:
            os.makedirs(out_filename)
        else:
            base_path = os.path.split(out_filename)[0]
            if not os.path.exists(base_path):
                os.makedirs(base_path)
            with open(out_filename,'w') as out:
                out.write('')

    return out_filename


def make_numbered_prefix(file_number,number_digits=5):
    """
    returns a number string designed to be used in the prefix of
    systematic outputs.

    example use case
        "00001example_output_file.txt"
        "00002example_output_file.txt"

    Args:
        file_number (int): the number you want to prefix
        number_digits (int): minimum number of digits in the output
            string. Default is 5
    Returns:
        str: string of numbers with standard at least
            'number_digits' of digits
    """
    file_number = int( file_number )
    if file_number < 0:
        file_number_is_negative = True
    else:
        file_number_is_negative = False

    file_number_string = str( abs(file_number) )
    len_num_string = len(file_number_string)

    if len_num_string < number_digits:
        prefix = '0' * int(number_digits - len_num_string)
    else:
        prefix = ''

    if file_number_is_negative:
        prefix = '-' + prefix

    numbered_string = prefix + file_number_string
    return numbered_string


def convert_to(fname, format, output_dir=None, no_overwrite=False):
    """converts an image file to the specificed format
    "example.png" --> "example.jpg"

    Args:
        fname (str): the filename of the image you want to convert
        format (str): the format you want to convert to, acceptable options are:
            'png','jpg','tiff','tif','bmp','dib','jp2','jpe','jpeg','webp',
            'pbm','pgm','ppm','sr','ras'.
        output_dir (str,None): optional, a directory to save the reformatted
            image to. Default = None
        no_overwrite (bool): whether of not to prevent this function from
            overwriting a file if it already exists. see
            :prevent_overwrite:~`imagepypelines.prevent_overwrite` for
            more information

    Returns:
        str: the output filename that the converted file was saved to
    """
    # eg convert .PNG --> png if required
    format = format.lower().replace('.','')

    if format not in IMAGE_EXTENSIONS:
        raise TypeError("format must be one of {}".format(IMAGE_EXTENSIONS))

    file_path, ext = os.path.splitext(fname)
    if output_dir is None:
        out_name = file_path + '.' + format
    else:
        basename = os.path.basename(file_path)
        out_name = os.path.join(output_dir, basename + '.' + format)

    if no_overwrite:
        # check if the file exists
        out_name = prevent_overwrite(out_name)

    img = cv2.imread(fname)
    if img is None:
        raise RuntimeError("Unable to open up file {}".format(fname))

    cv2.imwrite(out_name, img)

    return out_name
