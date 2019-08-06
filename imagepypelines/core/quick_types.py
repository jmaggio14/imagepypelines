# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018-2019 Jeff Maggio, Nathan Dileas, Ryan Hartzell
#
from .BaseBlock import ArrayType, Same

__all__ = [
            'GRAY',
            'RGB',
            'RGBA',
            'ARRAY_1D',
            'ARRAY_2D',
            'ARRAY_3D',
            'ARRAY_4D',
            'ARRAY_ND',
            'SAME',
            ]
# --------------- Convienence Type Variables --------------------
GRAY = ArrayType([None,None])
"""convienence variable to create an io_map ArrayType for Grayscale imagery"""

RGB = ArrayType([None,None,3])
"""convienence variable to create an io_map ArrayType for Rgb imagery"""

RGBA = ArrayType([None,None,4])
"""convienence variable to create an io_map ArrayType for RGBA imagery"""

ARRAY_1D = ArrayType([None])
"""convienence variable to create an io_map ArrayType for 1D arrays"""

ARRAY_2D = ArrayType([None,None])
"""convienence variable to create an io_map ArrayType for 2D arrays"""

ARRAY_3D = ArrayType([None,None,None])
"""convienence variable to create an io_map ArrayType for 3D arrays"""

ARRAY_4D = ArrayType([None,None,None,None])
"""convienence variable to create an io_map ArrayType for 4D arrays"""

ARRAY_ND = ArrayType()
"""convienence variable to create an io_map ArrayType for arbitrarily shaped arrays"""

SAME = Same()
"""convienence variable to create an io_map ArrayType to return whatever type was passed in"""


# --------------- Convienence Type Variables --------------------
