# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018-2019 Jeff Maggio, Nathan Dileas, Ryan Hartzell
#
from .. import SimpleBlock
from .. import ArrayIn, ArrayOut
from .. import Same
from .. import norm_ab
import numpy as np

class Normalize(SimpleBlock):
    def __init__(self,a=0,b=1):
        self.a = a
        self.b = b
        io_kernel = [[ ArrayIn('arbitrary'),
                    ArrayOut('input_shape'),
                    "Normalizes the array to the given range, does not modify the shape" ]]
        super(Normalize, self).__init__(io_kernel)

    def process(self, datum):
        return norm_ab(datum,a,b)
