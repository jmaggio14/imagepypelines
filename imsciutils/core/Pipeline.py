from .. import core
from .. import ml
from .. import util


class Pipeline(object):
    """Pipeline object to apply a sequence of algorithms to input data

    """
    num = 1
    def __init__(self, blocks=[], name=None, verbose=True):
        if name is None:
            name = 'Pipeline' + str(self.num)

        self.verbose = verbose
        self.name = name
        self.printer = core.get_printer(self.name)

        if not self.verbose:
            self.printer.set_log_level( float('inf') )

        if not isinstance(blocks,list):
            error_msg = "'blocks' must be a list"
            self.printer.error(error_msg)
            raise TypeError(error_msg)

        self.blocks = blocks
        self.num += 1

    def add(self, block):
        """adds processing block to the pipeline processing chain"""
        if not isinstance(block, ml.BaseBlock):
            error_msg = "'block' must be a subclass of iu.ml.Block"
            self.printer.error(error_msg)
            raise TypeError(error_msg)

        self.blocks.append(block)

    def train(self, x_data):
        """trains all processing blocks in the pipeline"""
        timer = util.Timer()
        for block in self.blocks:
            self.printer.info("{}: training on {} datums".format(block.name,
                                                                len(x_data)))
            block.run_train(x_data)
            x_data = block.run_process(x_data)
            self.printer.info("{}: trained in {}seconds".format(block.name,
                                                                timer.lap()))
        self.printer.info("all blocks trained: {}seconds".format(timer.time()))
        return x_data

    def process(self, x_data):
        """processed x_data by sequentially running data through all blocks"""
        timer = util.Timer()
        for block in self.blocks:
            self.printer.info("{}: processing {} datums...".format(block.name,
                                                               len(x_data)))
            x_data = block.run_process(x_data)
            self.printer.info("{}: trained in {}seconds".format(block.name,
                                                                timer.lap()))

        return x_data
