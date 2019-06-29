# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018-2019 Jeff Maggio, Nathan Dileas, Ryan Hartzell
from ..Logger import get_logger
from .BaseBlock import BaseBlock
from .BaseBlock import ArrayType
from .BaseBlock import Incompatible
from .Exceptions import CrackedPipeline
from .Exceptions import IncompatibleTypes
from .util import Timer


import collections
import pickle
import copy
import numpy as np
from termcolor import cprint
from uuid import uuid4

PIPELINE_NAMES = {}
INCOMPATIBLE = (Incompatible(),)

def name_pipeline(name,obj):
    """

    """
    if name is None:
        name = obj.__class__.__name__

    global PIPELINE_NAMES
    if name in PIPELINE_NAMES:
        PIPELINE_NAMES[name] += 1
    else:
        PIPELINE_NAMES[name] = 1

    return name + ('-%s' % PIPELINE_NAMES[name])

def get_types(data):
    """Retrieves the block data type of the input datum"""
    def _get_types():
        for datum in data:
            if isinstance(datum,np.ndarray):
                yield (ArrayType(datum.shape),)
            else:
                yield (type(datum),)

    return set( _get_types() )

class Pipeline(object):
    """
        Pipeline object to apply a sequence of algorithms to input data

        Pipelines pass data between block objects and validate the integrity
        of a data processing pipeline. It is intended to be a quick, flexible,
        and modular approach to creating a processing graph. It also contains
        helper functions for documentation and saving these pipelines for use by
        other researchers/users.

        Args:
            blocks(list): list of blocks to instantiate this pipeline with,
                shortcut to the 'add' function. defaults to []
            name(str): name for this pipeline that will be enumerated to be
                unique, defaults to the name of the Pipeline-<index>


        Attributes:
            name(str): unique name for this pipeline
            blocks(list): list of block objects being used by this pipeline,
                in order of their processing sequence
            verbose(bool): whether or not this pipeline with print
                out its status
            enable_text_graph(bool): whether or not to print out a graph of
                pipeline blocks and outputs
            logger(ip.Logger): logger object for this pipeline,
                registered with 'name'
            uuid(str): universally unique hex id for this pipeline
    """
    def __init__(self,
                    blocks=[],
                    name=None,
                    skip_validation=False,
                    track_types=True,
                    debug=False):

        self.name = name_pipeline(name,self)
        self.skip_validation = skip_validation
        self.track_types = track_types
        self._debug = debug

        self.logger = get_logger(self.name)
        self.blocks = []
        self.step_types = []

        if isinstance(blocks, (list,tuple)):
            for b in blocks:
                self.add(b)
        else:
            raise TypeError("'blocks' must be a list")

        self.uuid = uuid4().hex

    # ================== validation / debugging functions ==================
    def validate(self,data):
        """validates the integrity of the pipeline

        verifies all input-output shapes are compatible with each other

        Developer Note:
            this function could use a full refactor, especially with regards
            to printouts when an error is raised - Jeff

            Type comparison between Blocks is complicated and I suspect more
            bugs are still yet to be discovered.

        Raises:
            TypeError: if 'data' isn't a list or tuple
            RuntimeError: if more than one block in the pipeline has the same
                name, or not all objects in the block list are BaseBlock
                subclasses
        """
        # assert that every element in the blocks list is a BaseBlock subclass
        if not all(isinstance(b,BaseBlock) for b in self.blocks):
            error_msg = \
               "All elements of the pipeline must be subclasses of ip.BaseBlock"
            raise RuntimeError(error_msg)

        # make sure data is a list
        if not isinstance(data,list):
            raise TypeError("'data' must be list")

        # make sure every block has a unique name
        if len(set(self.names)) != len(self.names):
            error_msg = "every block in the pipeline must have a different name"
            raise RuntimeError(error_msg)

        predicted_type_chains = self.predict_type_chain(data)

        # print incompatability warnings
        for pred_chain in predicted_type_chains:
            vals = tuple(pred_chain.values())
            if INCOMPATIBLE in vals:
                idx = vals.index(INCOMPATIBLE) - 1
                block1 = self.blocks[idx-1]
                block2 = self.blocks[idx]

                msg = "pipeline_input={}: predicted incompatability between {}(output={})-->{}(inputs={})"
                msg = msg.format(pred_chain['pipeline_input'],
                                    block1.name,
                                    pred_chain[block1.name],
                                    block2.name,
                                    block2.io_map.inputs)
                self.logger.warning(msg)

        if self.debug:
            self._text_graph(predicted_type_chains)

    def predict_type_chain(self,data):
        """Predict the types at each stage of the pipeline
        """
        data_types = get_types(data)

        all_predicted_chains = []
        for input_ in data_types:
            predicted_chain = collections.OrderedDict(pipeline_input=input_)

            for block in self.blocks:
                if input_ == INCOMPATIBLE:
                    output_ = INCOMPATIBLE
                else:
                    try:
                        output_ = block.io_map.output( input_ )
                    except IncompatibleTypes as e:
                        output_ = INCOMPATIBLE

                predicted_chain[str(block)] = output_
                input_ = output_

            predicted_chain['pipeline_output'] = ''
            all_predicted_chains.append(predicted_chain)

        return all_predicted_chains

    def _text_graph(self,type_chains):
        for i,chain in enumerate(type_chains):
            print("-----------------| type-chain%s |-----------------" % i)
            buf = ' ' * 6
            for b,output in chain.items():
                color = 'red' if output == INCOMPATIBLE else None
                output = ',  '.join(str(s) for s in output)
                out_str = '  {buf}|\n  {buf}|{out}\n  {buf}|'
                out_str = out_str.format(buf=' ' * 6, out=output)

                cprint('  {}'.format(b), color)
                if b == 'pipeline_output':
                    break
                cprint(out_str, color)

    def debug(self):
        """Enables debug mode which turns on all printouts for this pipeline
        to aide in debugging
        """
        self._debug = True
        return self

    def graph(self):
        """TODO: Placeholder function for @Ryan to create"""
        pass

    # ================== pipeline processing functions ==================
    def _pair_blocks(self):
        """
        pairs every block with this pipeline in preparation for processing
        """
        for b in self.blocks:
            b._pipeline_pair(self)

    def _step(self):
        """
        """
        # retrieve block for this step
        block = self.blocks[self.step_index]

        if self.track_types:
            # check type of all data in this step
            step_types = get_types(self.step_data)
            self.step_types.append(step_types)

            try:
                for step_type in step_types:
                    block.io_map.output(step_type)
            except IncompatibleTypes as e:
                msg = "not all {} outputs ({}) compatible with {}'s IoMap inputs({}). attempting to compute regardless..."
                msg = msg.format(self.blocks[self.step_index-1], step_types, block, block.io_map.inputs )
                self.logger.warning(msg)

        self.step_data,self.step_labels = self._run_block(block,
                                                            self.step_data,
                                                            self.step_labels)

        self.step_index += 1
        return self.step_data,self.step_labels

    def _run_block(self,block,data,labels=None):
        t = Timer()

        # processing data using the block
        processed,labels = block._pipeline_process(data,labels)

        # printing out process time to the terminal
        b_time = t.lap() # processing time for this block
        datum_time_ms = round(1000 * b_time / len(data), 3)
        debug_msg = "{}: processed {}datums in {} seconds".format(block.name,
                                                                    len(data),
                                                                    b_time)
        datum_msg = " (approx {}ms per datum)".format(datum_time_ms)
        self.logger.debug(debug_msg, datum_msg)
        return processed,labels

    # ================== processing functions
    def _before_process(self,data,labels=None):
        self._pair_blocks()
        # check to make sure all blocks have been trained if required
        if not self.trained:
            for b in self.blocks:
                if not b.trained:
                    err_msg = "requires training, but hasn't yet been trained"
                    self.logger.error("{}: ".format(b.name), err_msg)

            raise RuntimeError("you must run Pipeline.train before processing")

        if not self.skip_validation:
            # validate pipeline integrity
            self.validate(data)

        # set initial conditions for the _step function
        self.step_index = 0
        self.step_data = data
        self.step_labels = labels
        self.step_types = []

    def _process(self,data):
        # step through each block
        for i in range( len(self.blocks) ):
            self._step()

    def _after_process(self):
        # remove step data and labels memory footprint
        if self.track_types:
            # append the pipeline output to the type chain
            self.step_types.append( get_types(self.step_data) )

        self.step_data = None
        self.step_labels = None

    def process(self,data):
        self._before_process(data,None)
        self._process(data)
        processed = self.step_data
        self._after_process()
        return processed

    # ================== training functions
    def _before_train(self,data,labels=None):
        self._pair_blocks()
        if not self.skip_validation:
            # validate pipeline integrity
            self.validate(data)

        # set initial conditions for the _step function
        self.step_index = 0
        self.step_data = data
        self.step_labels = labels
        self.step_types = []

    def _train(self,data,labels=None):
        # TODO Add a check to see throw an error if self.requires_labels == True
        # and no labels are passed into this function
        t = Timer()
        for b in self.blocks:
            self.logger.debug("training {}...".format(b.name))
            b._pipeline_train(self.step_data,self.step_labels)
            self._step() #step the block processing forward

            self.logger.info("{}: trained in {} sec".format(b.name,t.lap()))

        self.logger.info("Pipeline trained in {}seconds".format(t.time()))

    def _after_train(self):
        self._after_process()

    def train(self,data,labels=None):
        self._before_train(data,labels)
        self._train(data,labels)

        processed,labels = self.step_data,self.step_labels
        self._after_train()
        return processed,labels

    # ================== utility functions / properties ==================
    def save(self, filename=None):
        """
        Pickles and saves the entire pipeline as a pickled object, so it can
        be used by others or at another time

        Args:
            filename (string): filename to save pipeline to, defaults to
                saving the pipeline to the current directory
        Returns:
            str: the filename the pipeline was saved to
        """
        if filename is None:
            filename = os.path.join( os.getcwd(), self.name + '.pck' )

        with open(filename, 'wb') as f:
            pickle.dump(self, f)

        return filename

    def rename(self, name):
        assert isinstance(name, str), "name must be a string"
        self.name = name
        self.logger = get_logger(self.name)
        return self

    @property
    def names(self):
        """Returns the names of all blocks"""
        return [b.name for b in self.blocks]

    @property
    def trained(self):
        """Returns whether or not this pipeline has been trained"""
        return all(b.trained for b in self.blocks)

    @property
    def requires_labels(self):
        """Returns whether or not this pipeline requires labels"""
        return any(b.requires_labels for b in self.blocks)

    def __str__(self):
        out = "<{}>: '{}'  ".format(self.__class__.__name__,self.name) \
                + '(' + "->".join(b.name for b in self.blocks) + ')'
        return out

    def __repr__(self):
        return str(self)

    def __del__(self):
        for b in self.blocks:
            del b

        del self.blocks
        del self

    # ======== block list manipulation / List functionality functions ========
    def add(self, block):
        """Adds processing block to the pipeline processing chain

        Args:
            block (ip.BaseBlock): block object to add to this pipeline

        Returns:
            None

        Raise:
            TypeError: if 'block' is not a subclass of BaseBlock
        """
        # checking to make sure block is a real block
        if not isinstance(block, BaseBlock):
            error_msg = "'block' must be a subclass of ip.BaseBlock"
            self.logger.error(error_msg)
            raise TypeError(error_msg)

        self.logger.info("adding block {} to the pipeline".format(block.name))
        self.blocks.append(block)

    def insert(self, index, block):
        """Inserts processing block into the pipeline processing chain

        Args:
            index (int): index at which block object is to be inserted
            block (ip.BaseBlock): block object to add to this pipeline

        Returns:
            None

        Raises:
            TypeError: if 'block' is not a subclass of BaseBlock, or 'index'
                is not instance of int
        """
        # checking to make sure block is a real block
        if not isinstance(block, BaseBlock):
            error_msg = "'block' must be a subclass of ip.BaseBlock"
            self.logger.error(error_msg)
            raise TypeError(error_msg)

        # checking to make sure index is integer
        if not isinstance(index, int):
            error_msg = "can't add block to pipeline -'index' must be an int"
            self.logger.error(error_msg)
            raise TypeError(error_msg)

        self.logger.info("inserting block {0} into pipeline at index {1}"\
                                    .format(block.name, index))
        self.blocks.insert(index, block)

    def remove(self, block_name):
        """removes processing block from the pipeline processing chain

        Args:
            block_name (str): unique string name of block object to remove

        Returns:
            None

        Raise:
            TypeError: if 'block_name' is not an instance of str
            ValueError: if 'block_name' is not member of list self.names
        """
        # checking to make sure block_name is string
        if (not isinstance(block_name, str)):
            error_msg = "'block_name' must be a string"
            self.logger.error(error_msg)
            raise TypeError(error_msg)

        # checking to make sure block_name is member of self.names
        if (block_name in self.names):
            error_msg = "'block_name' must be member of list self.names"
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        self.logger.info("removing block {} from the pipeline".format(block_name))

        # get index from block name and delete corresponding item from self.blocks
        i = self.names.index(block_name)
        self.__delitem__(i)

    def copy(self):
        """Provides deepcopy of pipeline processing chain

        Args:
            None

        Returns:
            deepcopy: a deepcopy of the entire pipeline instance, 'self'

        Raise:
            None
        """
        # returns a deepcopy of entire pipeline (this will be useful for cache?)
        return copy.deepcopy(self)

    def clear(self):
        """Clears all processing blocks from the pipeline processing chain

        Args:
            None

        Returns:
            None

        Raise:
            None
        """
        # cycle through blocks and handle individual deletion, reset empty list
        for i in range(len(self.blocks)):
            self.__delitem__(i)

        self.blocks = []

    def join(self,pipeline):
        """Adds the blocks from an input pipeline to the current pipeline

        Args:
            pipeline(ip.Pipeline): a valid pipeline object containing blocks

        Returns:
            None

        Raise:
            None

        """
        for b in pipeline.blocks:
            self.add(b)

    def __delitem__(self, i):
        # Method for cleaning up file io and multiprocessing with caching revamp
        if not isinstance(i, int):
            error_msg = "'i' must be an int"
            self.logger.error(error_msg)
            raise TypeError(error_msg)

        del self.blocks[i]

    def __getitem__(self,index):
        return self.blocks[index]

    def __setitem__(self,index,block):
        if not isinstance(block, BaseBlock):
            error_msg = "'block' must be a subclass of ip.BaseBlock"
            self.logger.error(error_msg)
            raise TypeError(error_msg)

        self.logger.info("{} replaced with {}".format(self.blocks[index],block.name))
        self.blocks[index] = block

    def __iter__(self):
        """generator to return all blocks in the pipeline"""
        return (b for b in self.blocks)

    def __next__(self):
        """yields next item of self.blocks via generator"""
        for b in self.blocks:
            yield b

    def __getstate__(self):
        """pickle state retrieval function, its most important use is to
        delete the copied uuid to prevent potential issues from improper
        restoration

        Note:
            If you overload this function, it's imperative that you call this
            function via super().__getstate__(state), or otherwise return
            a state dictionary without a uuid
        """
        state = self.__dict__.copy()
        del state['uuid']

    def __setstate__(self, state):
        """pickle restoration function, its most important use is to generate
        a new uuid for the copied or deserialized object

        Note:
            If you overload this function, it's imperative that you call this
            function via super().__setstate__(state), or otherwise create a
            new unique uuid for the restored Pipeline _self.uuid = uuid4().hex
        """
        self.__dict__.update(state)
        # create a new uuid for this instance, since it's technically a
        # different object
        self.uuid = uuid4().hex
