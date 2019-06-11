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

class Divide(SimpleBlock):
    def __init__(self,divisor):
        assert isinstance(divisor,(int,float,np.ndarray))
        self.divisor = divisor
        io_kernel = {
                    [ArrayIn('arbitrary'),
                        ArrayOut('input_shape'),
                        "divide the input by the divisor"],
                    [int,
                        float,
                        "divide the input by the divisor"],
                    [float,
                        float,
                        "divide the input by the divisor"],
                    }
        super(Divide,self).__init__(io_kernel)

    def process(self, datum):
        return datum / self.divisor
