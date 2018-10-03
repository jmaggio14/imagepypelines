#
# @Email:  jmaggio14@gmail.com
#
# MIT License: https://github.com/jmaggio14/imsciutils/blob/master/LICENSE
#
# Copyright (c) 2018 Jeff Maggio, Nathan Dileas, Ryan Hartzell
#
from .Printer import get_printer
from .BaseBlock import BaseBlock
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
        self.printer = get_printer(self.name)

        # set log level to infinity if non-verbose is desired
        if not self.verbose:
            self.printer.set_log_level( float('inf') )

        # checking to make sure blocks is a list
        if not isinstance(blocks,list):
            error_msg = "'blocks' must be a list"
            self.printer.error(error_msg)
            raise TypeError(error_msg)

        self.blocks = blocks

    def add(self, block):
        """adds processing block to the pipeline processing chain"""
        # checking to make sure block is a real block
        if not isinstance(block, BaseBlock):
            error_msg = "'block' must be a subclass of iu.BaseBlock"
            self.printer.error(error_msg)
            raise TypeError(error_msg)

        # appends to instance block list
        self.blocks.append(block)

    def train(self, x_data):
        """trains all processing blocks in the pipeline"""
        timer = util.Timer()
        # runs training for each block and then processes the data for
        # the next block to train with
        for block in self.blocks:
            block.run_train(x_data)
            x_data = block.run_process(x_data)
            # printing for traceability
            self.printer.info("{}: trained in {} seconds on {} datums".format(
                                                                block.name,
                                                                timer.lap(),
                                                                len(x_data)))
        self.printer.info("all blocks trained: {}seconds".format(timer.time()))
        return x_data # trains all blocks if required

    def process(self, x_data):
        """processed x_data by sequentially running data through all blocks"""
        timer = util.Timer()
        # process the data through each block
        for block in self.blocks:
            x_data = block.run_process(x_data)
            # printing for traceability
            self.printer.info("{}: trained in {} seconds on {} datums".format(
                                                                block.name,
                                                                timer.lap(),
                                                                len(x_data)))

        return x_data
