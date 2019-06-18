# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018-2019 Jeff Maggio, Nathan Dileas, Ryan Hartzell
#

from .. import Pipeline
from .. import builtin_blocks as blocks

def LinearTransform(m,b):
    mult = blocks.Multiply(m)
    add = blocks.Add(b)

    pipeline = Pipeline([mult,add],name="LinearTransform")
    return pipeline
