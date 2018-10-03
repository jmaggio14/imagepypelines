#
# @Email:  jmaggio14@gmail.com
#
# MIT License: https://github.com/jmaggio14/imsciutils/blob/master/LICENSE
#
# Copyright (c) 2018 Jeff Maggio, Nathan Dileas, Ryan Hartzell
#
from .. import core
from .. import ml
from .. import util


class Pipeline(object):
    """Pipeline object to apply a sequence of algorithms to input data

    """
    extant = {}
    def __init__(self, blocks=[], name=None, verbose=True):
        if name is None:
            name = self.__class__.__name__

        # keeping track of names internally in a class variable
        if name in self.extant:
            self.extant[name] += 1
        else:
            self.extant[name] = 1
        name = name + str(self.extant[name])

        self.name = name
        self.verbose = verbose
        self.printer = core.get_printer(self.name)

        if not self.verbose:
            self.printer.set_log_level( float('inf') )

        if not isinstance(blocks,list):
            error_msg = "'blocks' must be a list"
            self.printer.error(error_msg)
            raise TypeError(error_msg)

        self.blocks = blocks

    def add(self, block):
        """adds processing block to the pipeline processing chain"""
        if not isinstance(block, ml.BaseBlock):
            error_msg = "'block' must be a subclass of iu.ml.BaseBlock"
            self.printer.error(error_msg)
            raise TypeError(error_msg)

        self.blocks.append(block) # add block

    def train(self, x_data):
        """trains all processing blocks in the pipeline"""
        timer = util.Timer()
        for block in self.blocks:
            block.run_train(x_data)
            x_data = block.run_process(x_data)
            self.printer.info("{}: trained in {} seconds on {} datums".format(
                                                                block.name,
                                                                timer.lap(),
                                                                len(x_data)))
        self.printer.info("all blocks trained: {}seconds".format(timer.time()))
        return x_data # trains all blocks if required

    def process(self, x_data):
        """processed x_data by sequentially running data through all blocks"""
        timer = util.Timer()
        for block in self.blocks:
            self.printer.info("{}: processing {} datums...".format(block.name,
                                                               len(x_data)))
            x_data = block.run_process(x_data)
            self.printer.info("{}: trained in {}seconds".format(block.name,
                                                                timer.lap()))

        return x_data # processes data
