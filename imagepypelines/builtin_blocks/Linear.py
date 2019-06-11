# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018-2019 Jeff Maggio, Nathan Dileas, Ryan Hartzell
#
from .. import SimpleBlock
from .. import ArrayIn, ArrayOut
import numpy as np

class Linear(SimpleBlock):
    def __init__(self,m,b):
        self.m = m
        if isinstance(b, (float,int)):
            b = float(b)
        self.b = b
        io_map = [
                    [ArrayIn("arbitrary"), ArrayOut("input_shape")]
                    [int, float]
                    [float, float]
                    ]
        super(Linear,self).__init__(io_map)

    def process(self, x):
        return (self.m * x) + self.b
