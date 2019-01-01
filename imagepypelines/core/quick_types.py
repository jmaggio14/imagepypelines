# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018 Jeff Maggio, Nathan Dileas, Ryan Hartzell
#
from .BaseBlock import ArrayType, Same

__all__ = [
            'GRAY',
            'RGB',
            'RGBA',
            '_1D',
            '_2D',
            '_3D',
            '_4D',
            '_ND',
            'SAME',
            ]
# --------------- Convienence Type Variables --------------------
GRAY = ArrayType([None,None])
"""convienence variable to create an io_map ArrayType for Grayscale imagery"""

RGB = ArrayType([None,None,3])
"""convienence variable to create an io_map ArrayType for Rgb imagery"""

RGBA = ArrayType([None,None,4])
"""convienence variable to create an io_map ArrayType for RGBA imagery"""

_1D = ArrayType([None])
"""convienence variable to create an io_map ArrayType for 1D arrays"""

_2D = ArrayType([None,None])
"""convienence variable to create an io_map ArrayType for 2D arrays"""

_3D = ArrayType([None,None,None])
"""convienence variable to create an io_map ArrayType for 3D arrays"""

_4D = ArrayType([None,None,None,None])
"""convienence variable to create an io_map ArrayType for 4D arrays"""

_ND = ArrayType()
"""convienence variable to create an io_map ArrayType for arbitrarily shaped arrays"""

SAME = Same()
"""convienence variable to create an io_map ArrayType to return whatever type was passed in"""
