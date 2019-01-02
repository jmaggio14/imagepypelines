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
import numpy as np

class Multiply(SimpleBlock):
    def __init__(self,term):
        assert isinstance(term,(int,float,np.ndarray))
        self.term = term
        io_map = {
                    ArrayType():Same(),
                    int:float,
                    float:float
                    }
        super(Divide,self).__init__(io_map)

    def process(self, datum):
        if isinstance(datum,int):
            datum = float(datum)

        return datum * self.term
