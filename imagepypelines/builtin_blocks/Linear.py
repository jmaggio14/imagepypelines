# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018-2019 Jeff Maggio, Nathan Dileas, Ryan Hartzell
#
from .. import SimpleBlock
from .. import ArrayType
from .. import ARRAY_ND, SAME
import numpy as np

class Linear(SimpleBlock):
    def __init__(self,m,b):
        self.m = m
        self.b = b
        io_map = {
                    ARRAY_ND:SAME,
                    int:float,
                    float:float
                    }
        super(Linear,self).__init__(io_map)

    def process(self, x):
        return (self.m * x) + self.b
