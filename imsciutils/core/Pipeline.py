#
# @Email:  jmaggio14@gmail.com
#
# MIT License: https://github.com/jmaggio14/imsciutils/blob/master/LICENSE
#
# Copyright (c) 2018 Jeff Maggio, Nathan Dileas, Ryan Hartzell
#
from __future__ import print_function
from .Printer import get_printer
from .Printer import set_global_printout_level
from .BaseBlock import BaseBlock
from .BaseBlock import ArrayType
from .Exceptions import CrackedPipeline
from .Exceptions import IncompatibleTypes
import collections
from .. import util
import pickle
import collections
import numpy as np

def restore_from_file(filename):
    """restores a pipeline from a pickled state

    Args:
        filename(str): the pipeline filename

    Returns:
        pipeline(iu.Pipeline): the loaded pipeline
    """
    pipeline = pickle.loads(filename)
    for b in pipeline.blocks:
        b.restore_from_serialization()

    return pipeline




def get_type(datum):
    if isinstance(datum,(str,)):
        return (str,)

    elif isinstance(datum,float):
        return (float,)

    elif isinstance(datum,int):
        return (int,)

    elif isinstance(datum,(np.ndarray,)):
        return (ArrayType(datum.shape,dtypes=datum.dtype),)

    else:
        msg = "only acceptable input datatypes are numpy arrays, floats, ints and strings"
        raise ValueError(msg)

class Pipeline(object):
    """Pipeline object to apply a sequence of algorithms to input data

    Pipelines pass data between block objects and validate the integrity
    of a data processing pipeline. it is intended to be a quick, flexible, and
    modular approach to creating a processing graph. It also contains helper
    functions for documentation and saving these pipelines for use by other
    researchers/users.

    Args:
        name(str): name for this pipeline that will be enumerated to be unique,
            defaults to the name of the subclass<index>
        blocks(list): list of blocks to instantiate this pipeline with, shortcut
            to the 'add' function. defaults to []
        verbose(bool): whether or not to enable printouts for this pipeline,
            defaults to True
        enable_text_graph(bool): whether or not to print out a graph of
            pipeline blocks and outputs

    Attributes:
        name(str): unique name for this pipeline
        blocks(list): list of block objects being used by this pipeline,
            in order of their processing sequence
        verbose(bool): verbose(bool): whether or not this pipeline with print
            out its status
        enable_text_graph(bool): whether or not to print out a graph of
            pipeline blocks and outputs
        printer(iu.Printer): printer object for this pipeline,
            registered with 'name'

    """
    EXTANT = {}
    def __init__(self,
                    blocks=[],
                    name=None,
                    verbose=True,
                    enable_text_graph=False):
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
        self.enable_text_graph = enable_text_graph
        self.printer = get_printer(self.name)
        self.names_to_extract = []
        self.intermediate_data = {}

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
        self.printer.info("adding block {} to the pipeline".format(block.name))
        self.blocks.append(block)

    def validate(self,data):
        """validates the integrity of the pipeline

        verifies all input-output shapes are compatible with each other

        type comparison for blocks is complicated

        Raises:
            CrackedPipeline: if there is a input-output shape
                incompatability
            TypeError: if 'data' isn't a list or tuple
        """

        # make sure data is a list
        if not isinstance(data,list):
            raise TypeError("'data' must be list")

        # JM: get shape of every datum
        # get unique shapes so we don't have to test every single shape
        data_types = set([get_type(datum) for datum in data])

        all_type_chains = []
        for data_type in data_types:
            type_chain = collections.OrderedDict(pipeline_input=data_type)
            input_type = data_type

            for block in self.blocks:
                try:
                    output_type = block.io_map.output_given_input(input_type)
                    broken_pair = False

                except IncompatibleTypes as e:
                    msg = []
                    for b,t in zip(list(type_chain.keys())[:-1],list(type_chain.values())[:-1]):
                        msg.append(b)
                        buf = ' ' * (len(msg[-1]) // 2)
                        msg.append("{}|".format(buf))
                        msg.append("{}| {}".format(buf,t))
                        msg.append("{}|".format(buf))

                    msg.append(list(type_chain.keys())[-1])
                    buf = ' ' * (len(msg[-1]) // 2)
                    msg.append("{}|".format(buf))
                    msg.append("{}X {}".format(buf,input_type))
                    msg.append("{}|".format(buf))
                    msg.append(str(block))
                    msg = '\n'.join(msg)
                    print(msg)
                    broken_pair = True

                type_chain[str(block)] = output_type
                input_type = output_type

                if broken_pair:
                    error_msg = "{} - acceptable types are {}".format(block.name,
                            list(block.io_map.inputs))
                    self.printer.error(error_msg)
                    raise CrackedPipeline("Incompatible types passed between blocks")

            type_chain['pipeline_output'] = ''
            all_type_chains.append(type_chain)

        if self.enable_text_graph:
            self._text_graph(all_type_chains)


    def train(self, data, labels=None):
        """trains every block in the pipeline

        Args:
            data(list): list of individual datums for the first block
                in the pipeline
            labels(list): list of labels for each datum, or None

        Returns:
            processed_data(list): list of processed training data
            labels(list): list of corresponding labels
        """
        self.validate(data)
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

    def process(self, data):
        """processes data using every block in the pipeline

        Args:
            data(list): list of individual datums for the first block
                in the pipeline

        Returns:
            processed_data(list): list of processed data
        """
        self.validate(data)
        self.intermediate_data = {}

        # JM: TODO: add auto batching and intermediate data retrieval
        # JM: verifying that all blocks have been trained
        num_initial_inputs = len(data)
        if not self.trained:
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
            data, _ = b._pipeline_process(data, None)
            b_time = t.lap() # processing time for this block
            # printing time for this block
            self.printer.debug("{}: processed {}datums in {} seconds".format(
                                    b.name,
                                    len(data),
                                    b_time),
                                " (approx {}ms per datum)".format(
                                    round(1000 * b_time / num, 3)))

            # JM: saving intermediate data to a dictionary so they can be
            # retrieved in self.get_intermediate_data()
            if b.name in self.intermediate_names:
                self.intermediate_data[b.name] = data


        self.printer.info("{} datums processed in {}ms".format(
                                                            num_initial_inputs,
                                                            t.time_ms()))

        return data

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

        # prepping each block for serialization
        for b in self.blocks:
            b.prep_for_serialization()

        if filename is None:
            filename = self.name + '.pck'
        with open(filename, 'wb') as f:
            pickle.dump(self, f)


    def _text_graph(self,type_chains):
        for chain in type_chains:
            print("type-chain1:")
            buf = ' ' * 6
            for b,output in chain.items():
                print('  ', b )
                if b == 'pipeline_output':
                    break
                print('  ',buf,'|')
                print('  ',buf,'|',',  '.join(str(o) for o in output))
                print('  ',buf,'|')

    def debug(self):
        """enables debug mode which turns on all printouts for this pipeline
        to aide in debugging
        """
        set_global_printout_level('debug')
        self.printer.set_log_level('debug')
        self.verbose = True
        self.enable_text_graph = True
        self.printer.warning("debug mode enabled!")
        return self

    def join(self,pipeline):
        """adds the blocks from the pipeline passed in to this pipeline
        """
        for b in pipeline.blocks:
            self.add(b)

    def set_intermediate_data(self,names_to_extract):
        self.intermediate_names = names_to_extract
        self.intermediate_data = {}

    def get_intermediate_data(self):
        return self.intermediate_data


    @property
    def names(self):
        """returns the names of all blocks"""
        return [b.name for b in self.blocks]

    @property
    def trained(self):
        """returns whether or not this pipeline has been trained"""
        return all(b.trained for b in self.blocks)

    @property
    def requires_labels(self):
        """returns whether or not this pipeline requires labels"""
        return any(b.requires_labels for b in self.blocks)

    def __str__(self):
        out = "{}: '{}'  ".format(self.__class__.__name__,self.name) \
                + '(' + "->".join(b.name for b in self.blocks) + ')'
        return out

    def __repr__(self):
        return str(self)

    def __getitem__(self,index):
        return self.blocks[index]

    def __setitem__(self,index,block):
        if not isinstance(block, BaseBlock):
            error_msg = "'block' must be a subclass of iu.BaseBlock"
            self.printer.error(error_msg)
            raise TypeError(error_msg)

        self.printer.info("{} replaced with {}".format(self.blocks[index],block.name))
        self.blocks[index] = block

    def __iter__(self):
        """generator to return all blocks in the pipeline"""
        for b in self.blocks:
            yield b
