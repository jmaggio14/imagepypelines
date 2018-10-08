#
# @Email:  jmaggio14@gmail.com
#
# MIT License: https://github.com/jmaggio14/imsciutils/blob/master/LICENSE
#
# Copyright (c) 2018 Jeff Maggio, Nathan Dileas, Ryan Hartzell
#
from .Printer import get_printer
from .BaseBlock import BaseBlock
from .Exceptions import CrackedPipeline
from .. import util
import pickle
import collections


class BasePipeline(object):
    """Pipeline object to apply a sequence of algorithms to input data

    This base pipeline is fully functional and compatible with both supervised
    and unsupervised setups, however it's highly reccomended that you use it's
    children 'Pipeline' and 'SupervisedPipeline'

    Pipelines pass data between block objects and validate the integrity
    of a data processing pipeline. it is intended to be a quick, flexible, and
    module approach to creating a processing graph. It also contains helper
    functions for documentation and saving these pipelines for use by other
    researchers/users.

    Args:
        name(str): name for this pipeline that will be enumerated to be unique,
            defaults to the name of the subclass<index>
        blocks(list): list of blocks to instantiate this pipeline with, shortcut
            to the 'add' function. defaults to []
        verbose(bool): whether or not to enable printouts for this pipeline,
            defaults to True

    Attributes:
        name(str): unique name for this pipeline
        blocks(list): list of block objects being used by this pipeline,
            in order of their processing sequence
        verbose(bool): verbose(bool): whether or not this pipeline with print
            out its status
        printer(iu.Printer): printer object for this pipeline,
            registered with 'name'

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
            self.printer.set_log_level(float('inf'))

        # checking to make sure blocks is a list
        if not isinstance(blocks, list):
            error_msg = "'blocks' must be a list"
            self.printer.error(error_msg)
            raise TypeError(error_msg)

        self.blocks = []
        for b in blocks:
            self.add(b)

    def add(self, block):
        """adds processing block to the pipeline processing chain

        Args:
            block (iu.BaseBlock): block object to add to this pipeline

        Returns:
            None

        Raise:
            TypeError: if 'block' is not a subclass of BaseBlock
        """
        # checking to make sure block is a real block
        if not isinstance(block, BaseBlock):
            error_msg = "'block' must be a subclass of iu.BaseBlock"
            self.printer.error(error_msg)
            raise TypeError(error_msg)

        # appends to instance block list
        self.blocks.append(block)

    def validate(self):
        """validates the integrity of the pipeline

        verifies all input-output shapes are compatible with each other

        Raises:
            CrackedPipeline: if there is a input-output shape
                incompatability
        """
        # JM: get output_shapes, last block's output is irrelevant
        out_blocks = [b for b in self.blocks[:-1]]
        # JM: get input blocks, first block's input is irrelevant
        in_blocks = [b for b in self.blocks[1:]]

        broken_pairs = []
        for b_out, b_in in zip(out_blocks, in_blocks):
            # if input_block accepts any type, skip this block-pair check
            if None in b_in.input_shape:
                continue

            for out in out_block.output_shape:
                is_broken = False
                if out not in in_block.input_shape:
                    error_msg = "{} out {} must be among {}'s inputs : {}"\
                        .format(b_out.name, out, b_in.name, b_in.input_shape)
                    self.printer.error(error_msg)
                    is_broken = True

                if is_broken:
                    broken_pairs.append( [b_out,b_in] )

        # raise cracked pipeline error if the pipeline will break
        if len(broken_pairs) > 0:
            raise CrackedPipeline(broken_pairs,self.name)

    def train(self, data, labels):
        """trains every block in the pipeline

        Args:
            data(list): list of individual datums for the first block
                in the pipeline
            labels(list): list of labels for each datum

        Returns:
            processed_data(list): list of processed training data
            labels(list): list of corresponding labels
        """
        self.validate()
        t = util.Timer()

        for b in self.blocks:
            b._pipeline_train(data, labels)
            data, labels = b._pipeline_process(data, labels)

            # print for traceability
            train_time = t.lap()
            self.printer.info("{}: trained in {} sec".format(
                b.name,
                train_time,
            ))

        self.printer.info("training complete")

        return data, labels

    def process(self, data, labels):
        """processes data using every block in the pipeline

        Args:
            data(list): list of individual datums for the first block
                in the pipeline
            labels(list): list of labels for each datum

        Returns:
            processed_data(list): list of processed data
            labels(list): list of corresponding labels
        """
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
            num = len(data)
            data, labels = b._pipeline_process(data, labels)
            b_time = t.lap()  # time for this block
            # printing time for this block
            self.printer.info("{}: processed in {} seconds".format(b.name,
                                                                   b_time))
            # printing individual datum time
            self.printer.debug("(approx {}sec per datum)".format(
                round(b_time / num, 3)))

        self.printer.info("all data processed in {} seconds".format(t.time()))

        return data, labels

    def graph(self):
        """TODO: Placeholder function for @Ryan to create"""
        pass

    def save(self, filename=None):
        """
        pickles and saves the entire pipeline as a pickled object, so it can
        be used by others or at another time

        Args:
            filename (string): filename to save pipeline to, defaults to
                pipeline.name + '.pck'
        """
        if filename is None:
            filename = self.name + '.pck'
        with open(filename, 'wb') as f:
            pickle.dump(self, f)


class SupervisedPipeline(BasePipeline):
    """Pipeline Subclass that requires the use of labels for training

    Pipelines pass data between block objects and validate the integrity
    of a data processing pipeline. it is intended to be a quick, flexible, and
    module approach to creating a processing graph. It also contains helper
    functions for documentation and saving these pipelines for use by other
    researchers/users.

    Args:
        name(str): name for this pipeline that will be enumerated to be unique,
            defaults to the name of the subclass<index>
        blocks(list): list of blocks to instantiate this pipeline with, shortcut
            to the 'add' function. defaults to []
        verbose(bool): whether or not to enable printouts for this pipeline,
            defaults to True

    Attributes:
        name(str): unique name for this pipeline
        blocks(list): list of block objects being used by this pipeline,
            in order of their processing sequence
        verbose(bool): verbose(bool): whether or not this pipeline with print
            out its status
        printer(iu.Printer): printer object for this pipeline,
            registered with 'name'
    """
    def train(self,data,labels):
        """trains every block in the pipeline

        Args:
            data(list): list of individual datums for the first block
                in the pipeline
            labels(list): list of labels for each datum

        Returns:
            processed_data(list): list of processed training data
            labels(list): list of corresponding labels
        """
        if len(data) != len(labels):
            error_msg = "there must be an equal number of datapoints ({}) and"\
                        + "labels ({})".format(len(data),len(labels))
            self.printer.error(error_msg)
            raise RuntimeError(error_msg)

        processed,labels = super(SupervisedPipeline,self).train(data,labels)
        return processed, labels

    def process(self,data,labels):
        """processes data using every block in the pipeline

        Args:
            data(list): list of individual datums for the first block
                in the pipeline
            labels(list): list of labels for each datum

        Returns:
            processed_data(list): list of processed data
            labels(list): list of corresponding labels
        """
        if len(data) != len(labels):
            error_msg = "there must be an equal number of datapoints ({}) and"\
                        + "labels ({})".format(len(data),len(labels))
            self.printer.error(error_msg)
            raise RuntimeError(error_msg)

        processed,labels = super(SupervisedPipeline,self).process(data,labels)
        return processed, labels



class Pipeline(BasePipeline):
    """Pipeline subclass that does not require using labels whatsoever

    Pipelines pass data between block objects and validate the integrity
    of a data processing pipeline. it is intended to be a quick, flexible, and
    module approach to creating a processing graph. It also contains helper
    functions for documentation and saving these pipelines for use by other
    researchers/users.

    Args:
        name(str): name for this pipeline that will be enumerated to be unique,
            defaults to the name of the subclass<index>
        blocks(list): list of blocks to instantiate this pipeline with, shortcut
            to the 'add' function. defaults to []
        verbose(bool): whether or not to enable printouts for this pipeline,
            defaults to True

    Attributes:
        name(str): unique name for this pipeline
        blocks(list): list of block objects being used by this pipeline,
            in order of their processing sequence
        verbose(bool): verbose(bool): whether or not this pipeline with print
            out its status
        printer(iu.Printer): printer object for this pipeline,
            registered with 'name'
    """
    def train(self,data):
        """trains every block in the pipeline

        Args:
            data(list): list of individual datums for the first block
                in the pipeline

        Returns:
            processed_data(list): list of processed training data
        """
        processed,_ = super(SupervisedPipeline,self).train(data,None)
        return processed

    def process(self,data):
        """processes data using every block in the pipeline

        Args:
            data(list): list of individual datums for the first block
                in the pipeline

        Returns:
            processed_data(list): list of processed data
        """
        processed,_ = super(SupervisedPipeline,self).process(data,None)
        return processed




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
