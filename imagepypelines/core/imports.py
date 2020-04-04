# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018-2020 Jeff Maggio, Ryan Hartzell, and collaborators
#
import sys
from .. import MASTER_LOGGER


def import_tensorflow():
    """Direct tensorflow imports are discouraged for imagepypelines developers
    because it is not automatically installed alongside imagepypelines, and
    therefore may cause confusing errors to users.

    This function will check if tensorflow is installed and import it if
    possible. If tensorflow is not importable, it will print out installation
    instructions.

    Returns:
        module: module reference to tensorflow
    """
    try:
        import tensorflow as tf
    except ImportError:
        MASTER_LOGGER.error("tensorflow must be installed!")
        MASTER_LOGGER.error("'pip install tensorflow --user' (for CPU only)")
        MASTER_LOGGER.error("'pip install tensorflow-gpu --user' (for CPU+GPU)")
        MASTER_LOGGER.error("see README: https://github.com/jmaggio14/imagepypelines")
        sys.exit(1)

    return tf


def import_opencv():
    """Direct opencv imports are discouraged for imagepypelines developers
    because it is not automatically installed alongside imagepypelines, and
    therefore may cause confusing errors to users.

    This function will check if opencv is installed and import it if
    possible. If opencv is not importable, it will print out installation
    instructions.

    Returns:
        module: module reference to opencv
    """
    try:
        import cv2
    except ImportError:
        MASTER_LOGGER.error("imagepypelines requires opencv to be installed separately!")
        MASTER_LOGGER.error("see README: https://github.com/jmaggio14/imagepypelines")
        sys.exit(1)

    return cv2
