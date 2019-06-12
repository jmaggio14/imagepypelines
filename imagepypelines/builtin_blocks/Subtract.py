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

class Subtract(SimpleBlock):
    def __init__(self,term):
        assert isinstance(term,(int,float,np.ndarray))
        # forceably convert term to a float so integer datum
        # will consistently be a float
        if isinstance(term,int):
            term = float(term)
        self.term = term
        io_kernel = [
                        [ArrayIn("arbitrary"),
                            ArrayOut("input_shape"),
                            "adds the value to the array, leaving it's shape unchanged"],
                        [float, float],
                        [int, float],
                    ]
        super(Subtract, self).__init__(io_kernel)

    def process(self, datum):
        return datum - self.term
