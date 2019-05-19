import io
from .. import SimpleBlock, RGB, GRAY, ArrayType



class Array2Stream(SimpleBlock):
    def __init__(self):
        io_kernel = {ArrayType() : io.IOBase}
        super().__init__(io_kernel,
                            requires_labels=False,
                            requires_training=False)

    def process(self, datum):
        return io.BytesIO( bytes(datum) )
