import io
from .. import SimpleBlock, ArrayIn



class Array2Stream(SimpleBlock):
    def __init__(self):
        io_kernel = [[ArrayIn("arbitrary"),
                            io.IOBase,
                            "convert array to file stream"],
                            ]
        super().__init__(io_kernel,
                            requires_labels=False,
                            requires_training=False)

    def process(self, datum):
        return io.BytesIO( bytes(datum) )
