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
from ..Logger import error as iperror
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

################################################################################
#                                   Classes
################################################################################
# class CameraCapture(object):
#     """
#     object used to talk to pull imagery from UVC camera (webcam)
#
#     Args:
#         cam (int) = 0:
#             The camera's numerical index (on linux, this number is at the end of
#             the camera's file path eg: "/dev/video0")
#
#         fourcc (str) = "MJPG":
#              the codec used to encode images off the camera. Many UVC
#              camera device achieve highest frame rates with MJPG
#
#     Attributes:
#         cap (cv2.VideoCapture): the cv2 camera object
#         fourcc (str): the fourcc codec used for this camera
#         frame_number (int): the number of frame retrieval attempts
#
#     """
#
#     def __init__(self, cam=0, fourcc="MJPG"):
#         assert isinstance(cam, int), "cam' must be str or int"
#         assert isinstance(fourcc, str), "'fourcc' must be str"
#
#         # openning the camera
#         self.cam = int(cam)
#         self.open()
#
#         # setting the codec
#         self._changeable_settings = {
#             "width": cv2.CAP_PROP_FRAME_WIDTH,
#             "height": cv2.CAP_PROP_FRAME_HEIGHT,
#             "fps": cv2.CAP_PROP_FPS,
#             "brightness": cv2.CAP_PROP_BRIGHTNESS,
#             "contrast": cv2.CAP_PROP_CONTRAST,
#             "hue": cv2.CAP_PROP_HUE,
#             "gain": cv2.CAP_PROP_GAIN,
#             "exposure": cv2.CAP_PROP_EXPOSURE,
#             "fourcc": cv2.CAP_PROP_FOURCC}
#         self.change_setting('fourcc', fourcc)
#         self.fourcc = fourcc
#
#     def open(self):
#         self.cap = cv2.VideoCapture(self.cam)
#         self.frame_number = 0
#
#     def retrieve(self):
#         """
#         reads an image from the capture stream, returns a static debug
#         frame if it fails to read the frame
#
#         Args:
#             None
#
#         Returns:
#             np.ndarray: image frame from the Capture Stream
#         """
#         status = False
#         self.frame_number += 1
#
#         if self.cap.isOpened():
#             status, frame = self.cap.read()
#
#         elif not status or not self.cap.isOpened():
#             debug_message = "unable to read frame {0}, is camera connected?"\
#                 .format(self.frame_number)
#             raise CameraReadError(debug_message)
#
#         return frame
#
#     def metadata(self):
#         """
#         grabs all metadata from the frame using the metadata properties
#         and outputs it in an easy to use dictionary. also adds key
#         "capture_time", which is the time.time() at the time the metadata
#         is collected
#         WARNING - what metadata is available is dependent on what
#         camera is attached!
#
#         Args:
#             None
#
#         Returns:
#             dict: dictionary containing all metadata values
#         """
#         metadata = {
#             "width": self.__get_prop(cv2.CAP_PROP_FRAME_WIDTH),
#             "height": self.__get_prop(cv2.CAP_PROP_FRAME_HEIGHT),
#             "fps": self.__get_prop(cv2.CAP_PROP_FPS),
#             "contrast": self.__get_prop(cv2.CAP_PROP_CONTRAST),
#             "brightness": self.__get_prop(cv2.CAP_PROP_BRIGHTNESS),
#             "hue": self.__get_prop(cv2.CAP_PROP_HUE),
#             "gain": self.__get_prop(cv2.CAP_PROP_GAIN),
#             "exposure": self.__get_prop(cv2.CAP_PROP_EXPOSURE),
#             "writer_dims": (self.__get_prop(cv2.CAP_PROP_FRAME_HEIGHT),
#                             self.__get_prop(cv2.CAP_PROP_FRAME_WIDTH)),
#             "fourcc": self.fourcc,
#             "fourcc_val": self.__get_prop(cv2.CAP_PROP_FOURCC),
#             "capture_time": time.time(),
#             "frame_number": self.frame_number
#         }
#         return metadata
#
#     def change_setting(self, setting, value):
#         """changes a setting on the capture object
#         acceptable
#
#         Args:
#             setting (str): The setting to modify. Must be one of
#                 [width,height,fps,contrast,brightness,hue,gain,
#                 exposure,writer_dims,fourcc,fourcc_val,
#                 capture_time,frame_number]
#             value (variable): The value to switch the setting to
#
#         Returns:
#             None
#         """
#         if setting not in self._changeable_settings:
#             raise ValueError("settings must be one of {0}"
#                     .format(self._changeable_settings.keys()))
#
#
#         flag = self._changeable_settings[setting]
#         if setting == 'fourcc':
#             value = cv2.VideoWriter_fourcc(*value)
#         ret = self.cap.set(flag, value)
#         return ret
#
#     def __get_prop(self, flag):
#         """
#         gets a camera property
#         wrapper for VideoCapture.get function
#
#         Args:
#             flag (opencv constant): flag indicating what metadata to get
#
#         Returns:
#             the camera property requested
#         """
#
#         return self.cap.get(flag)
#
#     def close(self):
#         self.cap.release()
#
#
#
# class Emailer(object):
#     """
#     Goal is to build an object which can be used to automatically send emails
#     after a test or run completes.
#     """
#
#     def __init__(self,
#                 sender,
#                 recipients,
#                 subject="noreply: imagepypelines automated email",
#                 server_name='smtp.gmail.com',
#                 server_port=465):
#         self.subject = subject
#
#         # TODO verify that recipients are valid here
#         # ND: what is the rationale here?
#         # JM: for a line in get_msg: self.current_msg['To'] = ', '.join(self.recipients)
#         # my thinking a list or a single address can be passed in, it's admittedly a lil awk
#         if isinstance(recipients, str):
#             recipients = [recipients]
#
#         self.sender = sender
#         self.recipients = recipients
#         self.subject = subject
#         self.current_msg = None
#
#         self.server_name = server_name
#         self.server_port = server_port
#
#     def get_msg(self):
#         """
#         returns the current email message or creates a new one if one
#         is not already queued
#         """
#         if self.current_msg is not None:
#             return self.current_msg
#
#         self.current_msg = MIMEMultipart('alternative')
#         self.current_msg['Subject'] = self.subject
#         self.current_msg['To'] = ', '.join(self.recipients)
#         self.current_msg['From'] = self.sender
#         return self.current_msg
#
#     def attach(self, filename):
#         """
#         attaches a file to the email message
#         """
#         msg = self.get_msg()
#
#         if not os.path.isfile(filename):
#             iperror("file '{}' does not exist or is inaccessible,\
#                             skipping attachment!".format(filename))
#             return
#
#         with open(filename, 'rb') as fp:
#             msg.attach(fp.read())
#
#     def body(self, text):
#         """
#         sets the body of the current email message
#         """
#         if not isinstance(text, str):
#             iperror("unable to set body because text must be a str,\
#                     currently".format(type(text)))
#             return
#
#         msg = self.get_msg()
#         msg.attach(MIMEText(text, 'plain'))
#
#     def send(self, password=None):
#         """
#         sends the current message and clears the template so a new
#         message can be created
#         """
#         if password is None:
#             password = getpass.getpass()
#
#         msg = self.get_msg()
#
#         server = smtplib.SMTP_SSL(self.server_name, self.server_port)
#         server.ehlo()
#         server.login(self.sender, password)
#         server.send_message(msg)
#
#         self.current_msg = None
#
#     def close(self):
#         pass
#
#     def __enter__(self):
#         return self
#
#     def __exit__(self, exc_type, exc_val, exc_tb):
#         self.close()
#
#     def __del__(self):
#         self.close()
#
#
# # class ImageWriter(object):
# #     """
# #     Class that operates as a system that saves single frames to a
# #     specified output directory.
# #
# #     every new frame passed in will be saved in the following format:
# #         output_dir/000001example_filename.png
# #         output_dir/000002example_filename.png
# #         output_dir/000003example_filename.png
# #         ...
# #
# #     automatic resizing is also available
# #
# #     Args:
# #         output_dir (str):
# #             path to output directory that images will be saved to
# #         base_filename (str): default is 'image.png'
# #             filename common among all images, these will be incremented
# #             numerically with each new image saved
# #         size (tuple,None): Default is None
# #             size of the image if forced resizing is desired, or
# #             None if raw write is desired
# #         interpolation (cv2 interpolation type):
# #             Default is cv2.INTER_NEAREST
# #             interpolation method to be used if resizing is desired
# #
# #     """
# #
# #     def __init__(self, output_dir,
# #                          base_filename="image.png",
# #                          size=None,
# #                          interpolation=cv2.INTER_NEAREST):
# #
# #         assert isinstance(base_filename, str), "'base_filename' must be str"
# #         imagepypelines.util.interpolation_type_check(interpolation)
# #
# #         self.base_filename = base_filename
# #         self.size = size
# #         self.interpolation = interpolation
# #         self.image_number = 0
# #
# #     def write(self, frame):
# #         """
# #         writes an image frame to the specificed directory, forces
# #         resizing if specified when the class is instantiated
# #
# #         Args:
# #             frame (np.ndarray): frame to be saved to the output_dir
# #
# #         Returns:
# #             None
# #         """
# #         self.image_number += 1
# #         image_number = imagepypelines.util.make_numbered_prefix(self.image_number,6)
# #         out_filename = os.path.join(self.output_dir,
# #                                     image_number + self.base_filename)
# #
# #         if not isinstance(self.size, type(None)):
# #             frame = cv2.resize(frame,
# #                                dsize=(self.size[1], self.size[0]),
# #                                interpolation=self.interpolation)
# #
# #         cv2.imwrite(filename, frame)
# #
# #
# # class VideoWriter(object):
# #     """
# #     a wrapper class for the cv2 Video Writer:
# #     https://docs.opencv.org/3.0-beta/modules/videoio/doc/reading_and_writing_video.html#videowriter-fourcc
# #
# #     This class will take a series of single frame imagery and
# #     """
# #
# #     def __init__(self, filename="out_video.avi", fps=30.0, fourcc="XVID"):
# #         self.filename = imagepypelines.util.prevent_overwrite(filename)
# #         self._fourcc = fourcc
# #         self._fourcc_val = cv2.VideoWriter_fourcc(*self._fourcc)
# #         self._fps = float(fps)
# #         self.__is_initialized = False
# #
# #     def __init(self, size):
# #         """
# #         opens and initializes the videowriter
# #         """
# #         imagepypelines.info("initializing the VideoWriter...")
# #         self._h, self._w = size
# #         self.video_writer_kwargs = {"filename": self.filename,
# #                                     "fourcc": self._fourcc_val,
# #                                     "fps": self._fps,
# #                                     "frameSize": (self._w, self._h)
# #                                     }
# #         self.writer = cv2.VideoWriter(**self.video_writer_kwargs)
# #         self.__is_initialized = True
# #
# #     def write(self, frame):
# #         """
# #         writes a frame to the video file.
# #         automatically opens a video writer set to the input frame size
# #
# #         Args:
# #             frame (np.ndarray): input frame to save to file
# #
# #         Returns:
# #             None
# #         """
# #         if not self.__is_initialized:
# #             size = imagepypelines.frame_size(frame)
# #             self.__init(size)
# #
# #         if not self.writer.isOpened():
# #             self.writer.open(**self.video_writer_kwargs)
# #
# #         self.writer.write(frame)
# #
# #     def release(self):
# #         """
# #         closes the video writer
# #
# #         Args:
# #             None
# #
# #         Returns:
# #             None
# #         """
# #         self.writer.release()
