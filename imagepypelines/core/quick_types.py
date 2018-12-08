# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018 Jeff Maggio, Nathan Dileas, Ryan Hartzell
#
from .BaseBlock import ArrayType


# --------------- Convienence Shortcuts --------------------
GRAY = ArrayType([None,None])
"""convienence wrapper to create an io_map ArrayType for Grayscale imagery"""

RGB = ArrayType([None,None,3])
"""convienence wrapper to create an io_map ArrayType for Rgb imagery"""
