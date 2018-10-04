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
import pickle
import collections


class Pipeline(object):
    """Pipeline object to apply a sequence of algorithms to input data

    """
    EXTANT = {}
    def __init__(self, name=None, blocks=[], verbose=True):
        if name is None:
            name = self.__class__.__name__

        # keeping track of names internally in a class variable
        if name in self.EXTANT:
            self.EXTANT[name] += 1
        else:
            self.EXTANT[name] = 1
        name = name + str(self.EXTANT[name])

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

    def validate(self):
        #JM: get output_shapes, last block's output is irrelevant
        out_blocks = [b for b in self.blocks[:-1]]
        #JM: get input blocks, first block's input is irrelevant
        in_blocks = [b for b in self.blocks[1:]]

        raise_error = False
        for b_out,b_in in zip(out_blocks,in_blocks):
            if not (b_out.output_shape == b_in.input_shape):
                error_msg = "incompatible shapes between {}-->{}".format(
                                                                b_out.name,
                                                                b_in.name)
                self.printer.error(error_msg)
                raise_error = True

        # JM: TODO: make special exception for this purpose
        if raise_error:
            crit_msg = "All blocks must have compatible shapes"
            self.printer.critical(crit_msg)
            raise RuntimeError(crit_msg)

    def train(self,x_data):
        self.validate()
        

    def process(self,x_data):
        self.validate()
        # JM: TODO: add auto batching and intermediate data retrieval
        # JM: verifying that all blocks have been trained
        if not all(b.trained for b in self.blocks):
            for b in self.blocks:
                if b.trained:
                    continue
                err_msg = "requires training, but hasn't yet been trained"
                self.printer.error("{}: ".format(b.name), err_msg)
            raise RuntimeError("you must run Pipeline.train before processing")

        # JM: processing all data
        t = util.Timer()
        for b in self.blocks:
            num = len(x_data)
            x_data = b.run_process(x_data)
            b_time = t.lap() # time for this block
            # printing time for this block
            self.printer.info("{}: processed in {} seconds".format(b.name,
                                                                    b_time))
            # printing individual datum time
            self.printer.debug("(approx {}sec per datum)".format(
                                                        round(b_time / num,3)))



        self.printer.info("all data processed in {} seconds".format(t.time()))

        return x_data



    def graph(self):
        """TODO: Placeholder function for @Ryan to create"""
        pass

    def save(self,filename=None):
        if filename is None:
            filename = self.name + '.pck'
        with open(filename,'wb') as f:
            pickle.dump(self,f)

    #
    # def train(self, x_data):
    #     """trains all processing blocks in the pipeline"""
    #     timer = util.Timer()
    #     # runs training for each block and then processes the data for
    #     # the next block to train with
    #     for block in self.blocks:
    #         block.run_train(x_data)
    #         x_data = block.run_process(x_data)
    #         # printing for traceability
    #         self.printer.info("{}: trained in {} seconds on {} datums".format(
    #                                                             block.name,
    #                                                             timer.lap(),
    #                                                             len(x_data)))
    #     self.printer.info("all blocks trained: {}seconds".format(timer.time()))
    #     return x_data # trains all blocks if required
    #
    # def process(self, x_data):
    #     """processed x_data by sequentially running data through all blocks"""
    #     timer = util.Timer()
    #     # process the data through each block
    #     for block in self.blocks:
    #         x_data = block.run_process(x_data)
    #         # printing for traceability
    #         self.printer.info("{}: trained in {} seconds on {} datums".format(
    #                                                             block.name,
    #                                                             timer.lap(),
    #                                                             len(x_data)))
    #
    #     return x_data
