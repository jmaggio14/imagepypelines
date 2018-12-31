from .. import SimpleBlock
from .. import ArrayType
from .. import Same
import numpy as np

class Divide(SimpleBlock):
    def __init__(self,term):
        assert isinstance(term,(int,float,np.ndarray))
        self.term = term
        io_map = {
                    ArrayType():Same(),
                    int:float,
                    float:float
                    }
        super(Add,self).__init__(io_map)

    def process(self, datum):
        return datum / self.term
