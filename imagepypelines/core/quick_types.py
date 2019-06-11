# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018-2019 Jeff Maggio, Nathan Dileas, Ryan Hartzell
#
from .blockio import ArrayIn

__all__ = [
            'GRAY',
            'RGB',
            'RGBA',
            'ARRAY_1D',
            'ARRAY_2D',
            'ARRAY_3D',
            'ARRAY_4D',
            'ARRAY_ND',
            # 'SAME',
            ]
# --------------- Convienence Type Variables --------------------
GRAY = ArrayIn([None,None])
"""convienence variable to create an io_map ArrayIn for Grayscale imagery"""

RGB = ArrayIn([None,None,3])
"""convienence variable to create an io_map ArrayIn for Rgb imagery"""

RGBA = ArrayIn([None,None,4])
"""convienence variable to create an io_map ArrayIn for RGBA imagery"""

ARRAY_1D = ArrayIn([None])
"""convienence variable to create an io_map ArrayIn for 1D arrays"""

ARRAY_2D = ArrayIn([None,None])
"""convienence variable to create an io_map ArrayIn for 2D arrays"""

ARRAY_3D = ArrayIn([None,None,None])
"""convienence variable to create an io_map ArrayIn for 3D arrays"""

ARRAY_4D = ArrayIn([None,None,None,None])
"""convienence variable to create an io_map ArrayIn for 4D arrays"""

ARRAY_ND = ArrayIn()
"""convienence variable to create an io_map ArrayIn for arbitrarily shaped arrays"""

# SAME = Same()
# """convienence variable to create an io_map ArrayIn to return whatever type was passed in"""
