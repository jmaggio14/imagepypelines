# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018 Jeff Maggio, Nathan Dileas, Ryan Hartzell
#
from .. import SimpleBlock
from .. import ArrayType
from .. import Same
from .. import norm_ab
import numpy as np

class Normalize(SimpleBlock):
    def __init__(self,a=0,b=1):
        self.a = a
        self.b = b
        io_map = {ArrayType():Same()}
        super(Normalize,self).__init__(io_map)

    def process(self, datum):
        return norm_ab(datum,a,b)
