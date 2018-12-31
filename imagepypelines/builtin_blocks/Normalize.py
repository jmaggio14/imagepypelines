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
        super(Add,self).__init__(io_map)

    def process(self, datum):
        return norm_ab(datum,a,b)
