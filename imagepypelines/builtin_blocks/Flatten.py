from .. import SimpleBlock
from .. import ArrayType
from .. import Same
import numpy as np

class Flatten(SimpleBlock):
    def __init__(self):
        self.term = term
        io_map = {ArrayType():ArrayType([None])}
        super(Add,self).__init__(io_map)

    def process(self, datum):
        return datum.flatten()
