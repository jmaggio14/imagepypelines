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

class Add(SimpleBlock):
    def __init__(self,term):
        assert isinstance(term,(int,float,np.ndarray))
        # forceably convert term to a float so integer datum
        # will consistently be a float
        if isinstance(term,int):
            term = float(term)
        self.term = term

        io_map = {
                    ARRAY_ND:SAME,
                    int:float,
                    float:float
                    }
        notes = "adds a user-defined term to a numerical input"
        super(Add,self).__init__(io_map,notes=notes)

    def process(self, datum):
        return datum + self.term



# class Add(ip.SimpleBlock):
#     def __init__(self,term):
#         self.term = term
#         io_map = {
#                     ArrayType():Same(),
#                     int:float,
#                     float:float
#                     }
#         super(Add,self).__init__(io_map)
#
#     def process(self, datum):
#         return datum + self.term


# Subtract
# Multiply
# Divide
# Reshape
# Flatten
