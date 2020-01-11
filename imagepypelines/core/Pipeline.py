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
import networkx as nx

INCOMPATIBLE = (Incompatible(),)


def get_types(data):
    """Retrieves the block data type of the input datum"""
    def _get_types():
        for datum in data:
            if isinstance(datum,np.ndarray):
                yield (ArrayType(datum.shape),)
            else:
                yield (type(datum),)

    return set( _get_types() )

class Input(BaseBlock):

    def __getitem__(self, key):

        return self._outputs[key]

    def __setitem__(self, key, val):

        self._outputs[key] = val

class Output(BaseBlock):

    def __getitem__(self, key):

        return self._inputs[key]

    def __setitem__(self, key, val):

        self._inputs[key] = val

class Pipeline(BaseBlock):

    def __init__(self, graph=None, name="Pipeline"):

        super().__init__(name)

        if graph is None:

            graph = nx.MultiDiGraph()

        self.graph = graph

        self._inputs = Input(name="Input")
        self._outputs = Output(name="Output")

        self.graph.add_node(self._inputs)
        self.graph.add_node(self._outputs)

    @property
    def inputs(self):

        return self._inputs

    @property
    def outputs(self):

        return self._outputs

    def __getitem__(self, key):

        return self._outputs[key]

    def __setitem__(self, key, val):

        self._inputs[key] = val

    @property
    def execution_order(self)

        return nx.topological_sort(self.graph)

    def process(self):

        print(f"Beginning processing of <{self.user_name}>'s internal Blocks...\n")

        for n in self.execution_order:

            for edge in self.graph.in_edges(n, keys=True):

                data = self.graph.get_edge_data(*edge)

                for target_key, source_key in data.items():

                    if isinstance(n, (BaseBlock, Pipeline)):

                        n.inputs[target_key] = edge[0].outputs[source_key]

                    else:

                        raise ValueError("Error out here if node is wrong type (should be other checks for this when adding nodes)")

            n.process()

            if isinstance(n, (Input)):

                print(f"Node = {n}   |   Params = {n.outputs}\n")

            elif isinstance(n, (Output)):

                print(f"Node = {n}   |   Results = {n.inputs}\n")

            elif isinstance(n, (Pipeline)):

                print(f"Node = {n}   |   Inputs = {n.inputs.outputs}   |   Outputs = {n.outputs.inputs}\n")

            else:

                print(f"Node = {n}   |   Inputs = {n.inputs}   |   Outputs = {n.outputs}\n")

            print(f"Finished! <{self.user_name}>'s results:\n\n{self.outputs.inputs}\n")

    def connect(self, source, target, source_key, target_key):

        # This can be expanded to accept iterable of the current argument pattern
        # i.e. self.graph.add_edges_from(iterable)

        self.graph.add_edges_from([(source, target, {target_key: source_key})])

    def disconnect(self):

        pass

    def lock(self):

        pass

    def unlock(self):

        pass

    def add_blocks(self, blocks):

        self.graph.add_nodes_from(blocks)

    def remove_blocks(self, blocks):

        pass

# FOR TESTING PURPOSES ONLY!!!
class Add(BaseBlock):

    def process(self):

        print(f"<{self.user_name}>'s inputs are resolved, processing them, adding to output dictionary...")

        # Make a simple adding operation
        self.outputs["result"] = (self.inputs["operand1"] + self.inputs["operand2"])

# class Pipeline(object):
#     """
#         Pipeline object to apply a sequence of algorithms to input data

#         Pipelines pass data between block objects and validate the integrity
#         of a data processing pipeline. It is intended to be a quick, flexible,
#         and modular approach to creating a processing graph. It also contains
#         helper functions for documentation and saving these pipelines for use by
#         other researchers/users.

#         Args:
#             blocks(list): list of blocks to instantiate this pipeline with,
#                 shortcut to the 'add' function. defaults to []
#             name(str): name for this pipeline that will be enumerated to be
#                 unique, defaults to the name of the Pipeline-<index>


#         Attributes:
#             name(str): unique name for this pipeline
#             blocks(list): list of block objects being used by this pipeline,
#                 in order of their processing sequence
#             verbose(bool): whether or not this pipeline with print
#                 out its status
#             enable_text_graph(bool): whether or not to print out a graph of
#                 pipeline blocks and outputs
#             logger(ip.Logger): logger object for this pipeline,
#                 registered with 'name'
#             uuid(str): universally unique hex id for this pipeline
#     """
#     def __init__(self,
#                     graph=[],
#                     name=None,
#                     skip_validation=False,
#                     track_types=True):

#          # this uuid will not change with copying or serialization
#          # as such it can be used to id which blocks are copies or unpickled
#          # versions of the original - it's metaphorical siblings
#         self.sibling_id = uuid4().hex
#         # setup absolutely unique id for this block
#         # this will change even if the block is copied or pickled
#         self.uuid = uuid4().hex
#         # ----------- building a unique name for this block ------------
#         # name is set up as follows
#         # <readable_name>-<sibling_id>-<uuid>
#         if name is None:
#             name = self.__class__.__name__
#         logger_name = self.__get_logger_name(name,
#                                                 self.sibling_id,
#                                                 self.uuid)

#         self.name = name
#         self.logger_name = logger_name
#         self.skip_validation = skip_validation
#         self.track_types = track_types

#         self.logger = get_logger(self.logger_name)
#         self.step_types = []

#         # Setup standard node/edge attribute dict - THIS WILL BE SETUP ELSEWHERE AND BE MORE COMPREHENSIVE!!!
#         self.std_node_attrs = {"Node Type": None,
#                               "Object": None
#                              }

#         self.std_edge_attrs = {"data_name": "default"}

#         # The reason we use add_nodes_from here is to cannibalize nodes on init
#         if isinstance(graph, (list,tuple)):

#             # must compute edges and add those!!!
#             self.graph = nx.MultiDiGraph()
#             # this works because the block's repr is used as hashable key!!! (but object is still directly accessible!!!!!!)
#             self.graph.add_edges_from( nx.path_graph(graph).edges )

#             # for loops to edit node and edge standard attribute dicts
#             for n in self.graph.nodes:

#                 # n.update(self.std_node_attrs)

#                 # THIS IS TO ILLUSTRATE THE BEHAVIOR I EXPLAINED - EACH NODE IS A BLOCK/PIPELINE OBJECT!!!!!!
#                 print(n)

#                 if isinstance(n, (ip.BaseBlock)):

#                     pass


#             # at this point we have a linear pipeline connected with single
#             #   edges, but we want the following representation:

#             # output = (a, b)  ---> edge1(a), edge2(b)

#         elif isinstance(graph, (Pipeline)):

#             # do Pipeline specific handling here (access graph and just use that)

#             self.graph = nx.MultiDiGraph()
#             self.graph.add_edges_from(graph.graph.edges)

#             # for loop to add node and edge standard attribute dicts

#         elif isinstance(graph, (nx.DiGraph, nx.MultiDiGraph)):

#             # just add this in like above, but more directly

#             self.graph = nx.MultiDiGraph()
#             self.graph.add_edges_from(graph.edges)

#             # for loop to add node and edge standard attribute dicts

#         elif isinstance(graph, (dict)):

#             # I forget how this differs but may be directly addable as well?
#             pass

#         else:
#             raise TypeError("'graph' must be an iterable")

#     #     # RUN BELOW FUNCS AFTER DOING TOPOLOGICAL ORDERING FIRST!!!

#     #     # Tentative objects for managing explicitly named input and output data
#     #     self._inputs = {}
#     #     self._outputs ={}
#     #     self._n_inputs = len(self.inputs.keys())
#     #     self._n_outputs = len(self.outputs.keys())
#     #
#     # @property
#     # def inputs(self):
#     #     # should return **kwargs input which was passed as data to first block?
#     #     self._inputs =
#     #     return self._inputs
#     #
#     # @property
#     # def outputs(self):
#     #     self._outputs =
#     #     return self._inputs
#     #
#     # @property
#     # def n_inputs(self):
#     #     self._n_inputs = len(self.inputs.keys())
#     #     return self._n_inputs
#     #
#     # @property
#     # def n_outputs(self):
#     #     self._n_outputs = len(self.outputs.keys())
#     #     return self._n_outputs

#     def debug(self):
#         return self
#     #     """Enables debug mode which turns on all printouts for this pipeline
#     #     to aide in debugging
#     #     """
#     #     self._debug = True
#     #     return self




#     # ================== Rudimentary graph framework ====================
#     def draw(self):
#         """TODO: Placeholder function for @Ryan to create"""
#         pass

#     def connect(self):
#         pass

#     def disconnect(self):
#         pass

#     def remove(self):
#         pass

#     def clear(self):
#         pass

#     def _get_topology(self):
#         """TODO: Sets up a priority/order of operations list for operations
#            on the graph sequentially from one point to another. Only operates on
#            THIS pipeline's highest level set of nodes. If a node is executed and
#            contains a pipeline, THAT pipeline will have its own order of
#            operations to follow for its own sub graph, and so on. RECURSIONNNN"""
#         pass


#     # ================== pipeline processing functions ==================
#     def _pair_blocks(self):
#         """
#         pairs every block with this pipeline in preparation for processing
#         """
#         for b in self.blocks:
#             b._pipeline_pair(self)

#     def _step(self):
#         """
#         """
#         # retrieve block for this step
#         block = self.blocks[self.step_index]

#         if self.track_types:
#             # check type of all data in this step
#             step_types = get_types(self.step_data)
#             self.step_types.append(step_types)

#             try:
#                 for step_type in step_types:
#                     block.io_map.output(step_type)
#             except IncompatibleTypes as e:
#                 msg = "not all {} outputs ({}) compatible with {}'s IoMap inputs({}). attempting to compute regardless..."
#                 msg = msg.format(self.blocks[self.step_index-1], step_types, block, block.io_map.inputs )
#                 self.logger.warning(msg)

#         self.step_data,self.step_labels = self._run_block(block,
#                                                             self.step_data,
#                                                             self.step_labels)

#         self.step_index += 1
#         return self.step_data,self.step_labels

#     def _run_block(self,block,data,labels=None):
#         t = Timer()

#         # processing data using the block
#         processed,labels = block._pipeline_process(data,labels)

#         # printing out process time to the terminal
#         b_time = t.lap() # processing time for this block
#         datum_time_ms = round(1000 * b_time / len(data), 3)
#         debug_msg = "{}: processed {}datums in {} seconds".format(block.name,
#                                                                     len(data),
#                                                                     b_time)
#         datum_msg = " (approx {}ms per datum)".format(datum_time_ms)
#         self.logger.debug(debug_msg, datum_msg)
#         return processed,labels

#     # ================== processing functions
#     def _before_process(self,data,labels=None):
#         self._pair_blocks()
#         # check to make sure all blocks have been trained if required
#         if not self.trained:
#             for b in self.blocks:
#                 if not b.trained:
#                     err_msg = "requires training, but hasn't yet been trained"
#                     self.logger.error("{}: ".format(b.name), err_msg)

#             raise RuntimeError("you must run Pipeline.train before processing")

#         if not self.skip_validation:
#             # validate pipeline integrity
#             self.validate(data)

#         # set initial conditions for the _step function
#         self.step_index = 0
#         self.step_data = data
#         self.step_labels = labels
#         self.step_types = []

#     def _process(self,data):
#         # step through each block
#         for i in range( len(self.blocks) ):
#             self._step()

#     def _after_process(self):
#         # remove step data and labels memory footprint
#         if self.track_types:
#             # append the pipeline output to the type chain
#             self.step_types.append( get_types(self.step_data) )

#         self.step_data = None
#         self.step_labels = None

#     def process(self,data):
#         self._before_process(data,None)
#         self._process(data)
#         processed = self.step_data
#         self._after_process()
#         return processed

#     # ================== training functions
#     def _before_train(self,data,labels=None):
#         self._pair_blocks()
#         if not self.skip_validation:
#             # validate pipeline integrity
#             self.validate(data)

#         # set initial conditions for the _step function
#         self.step_index = 0
#         self.step_data = data
#         self.step_labels = labels
#         self.step_types = []

#     def _train(self,data,labels=None):
#         # TODO Add a check to see throw an error if self.requires_labels == True
#         # and no labels are passed into this function
#         t = Timer()
#         for b in self.blocks:
#             self.logger.debug("training {}...".format(b.name))
#             b._pipeline_train(self.step_data,self.step_labels)
#             self._step() #step the block processing forward

#             self.logger.info("{}: trained in {} sec".format(b.name,t.lap()))

#         self.logger.info("Pipeline trained in {}seconds".format(t.time()))

#     def _after_train(self):
#         self._after_process()

#     def train(self,data,labels=None):
#         self._before_train(data,labels)
#         self._train(data,labels)

#         processed,labels = self.step_data,self.step_labels
#         self._after_train()
#         return processed,labels


#     # ================== utility functions / properties ==================
#     def save(self, filename=None):
#         """
#         Pickles and saves the entire pipeline as a pickled object, so it can
#         be used by others or at another time

#         Args:
#             filename (string): filename to save pipeline to, defaults to
#                 saving the pipeline to the current directory
#         Returns:
#             str: the filename the pipeline was saved to
#         """
#         if filename is None:
#             filename = os.path.join( os.getcwd(), self.name + '.pck' )

#         with open(filename, 'wb') as f:
#             pickle.dump(self, f)

#         return filename

#     def rename(self, name):
#         assert isinstance(name, str), "name must be a string"
#         self.name = name
#         self.logger_name = self.__get_logger_name(self.name,
#                                                     self.sibling_id,
#                                                     self.uuid)
#         self.logger = get_logger(self.logger_name)
#         return self

#     @property
#     def names(self):
#         """Returns the names of all blocks"""
#         return [b.name for b in self.blocks]

#     @property
#     def trained(self):
#         """Returns whether or not this pipeline has been trained"""
#         return all(b.trained for b in self.blocks)

#     @property
#     def requires_labels(self):
#         """Returns whether or not this pipeline requires labels"""
#         return any(b.requires_labels for b in self.blocks)

#     def __str__(self):
#         out = "<{}>: '{}'  ".format(self.__class__.__name__,self.name) \
#                 + '(' + "->".join(b.name for b in self.blocks) + ')'
#         return out

#     def __repr__(self):
#         return str(self)

#     # ======== block list manipulation / List functionality functions ========
#     def add(self, block):
#         """Adds processing block to the pipeline processing chain

#         Args:
#             block (ip.BaseBlock): block object to add to this pipeline

#         Returns:
#             None

#         Raise:
#             TypeError: if 'block' is not a subclass of BaseBlock
#         """
#         # checking to make sure block is a real block
#         if not isinstance(block, BaseBlock):
#             error_msg = "'block' must be a subclass of ip.BaseBlock"
#             self.logger.error(error_msg)
#             raise TypeError(error_msg)

#         self.logger.info("adding block {} to the pipeline".format(block.name))
#         self.blocks.append(block)

#     def insert(self, index, block):
#         """Inserts processing block into the pipeline processing chain

#         Args:
#             index (int): index at which block object is to be inserted
#             block (ip.BaseBlock): block object to add to this pipeline

#         Returns:
#             None

#         Raises:
#             TypeError: if 'block' is not a subclass of BaseBlock, or 'index'
#                 is not instance of int
#         """
#         # checking to make sure block is a real block
#         if not isinstance(block, BaseBlock):
#             error_msg = "'block' must be a subclass of ip.BaseBlock"
#             self.logger.error(error_msg)
#             raise TypeError(error_msg)

#         # checking to make sure index is integer
#         if not isinstance(index, int):
#             error_msg = "can't add block to pipeline -'index' must be an int"
#             self.logger.error(error_msg)
#             raise TypeError(error_msg)

#         self.logger.info("inserting block {0} into pipeline at index {1}"\
#                                     .format(block.name, index))
#         self.blocks.insert(index, block)

#     def remove(self, block_name):
#         """removes processing block from the pipeline processing chain

#         Args:
#             block_name (str): unique string name of block object to remove

#         Returns:
#             None

#         Raise:
#             TypeError: if 'block_name' is not an instance of str
#             ValueError: if 'block_name' is not member of list self.names
#         """
#         # checking to make sure block_name is string
#         if (not isinstance(block_name, str)):
#             error_msg = "'block_name' must be a string"
#             self.logger.error(error_msg)
#             raise TypeError(error_msg)

#         # checking to make sure block_name is member of self.names
#         if (block_name in self.names):
#             error_msg = "'block_name' must be member of list self.names"
#             self.logger.error(error_msg)
#             raise ValueError(error_msg)

#         self.logger.info("removing block {} from the pipeline".format(block_name))

#         # get index from block name and delete corresponding item from self.blocks
#         i = self.names.index(block_name)
#         self.__delitem__(i)

#     def copy(self):
#         """Provides deepcopy of pipeline processing chain

#         Args:
#             None

#         Returns:
#             deepcopy: a deepcopy of the entire pipeline instance, 'self'

#         Raise:
#             None
#         """
#         # returns a deepcopy of entire pipeline (this will be useful for cache?)
#         return copy.deepcopy(self)

#     def clear(self):
#         """Clears all processing blocks from the pipeline processing chain

#         Args:
#             None

#         Returns:
#             None

#         Raise:
#             None
#         """
#         # cycle through blocks and handle individual deletion, reset empty list
#         for i in range(len(self.blocks)):
#             self.__delitem__(i)

#         self.blocks = []

#     def join(self,pipeline):
#         """Adds the blocks from an input pipeline to the current pipeline

#         Args:
#             pipeline(ip.Pipeline): a valid pipeline object containing blocks

#         Returns:
#             None

#         Raise:
#             None

#         """
#         for b in pipeline.blocks:
#             self.add(b)

#     def __delitem__(self, i):
#         # Method for cleaning up file io and multiprocessing with caching revamp
#         if not isinstance(i, int):
#             error_msg = "'i' must be an int"
#             self.logger.error(error_msg)
#             raise TypeError(error_msg)

#         del self.blocks[i]

#     def __getitem__(self,index):
#         return self.blocks[index]

#     def __setitem__(self,index,block):
#         if not isinstance(block, BaseBlock):
#             error_msg = "'block' must be a subclass of ip.BaseBlock"
#             self.logger.error(error_msg)
#             raise TypeError(error_msg)

#         self.logger.info("{} replaced with {}".format(self.blocks[index],block.name))
#         self.blocks[index] = block

#     def __iter__(self):
#         """generator to return all blocks in the pipeline"""
#         return (b for b in self.blocks)

#     def __next__(self):
#         """yields next item of self.blocks via generator"""
#         for b in self.blocks:
#             yield b

#     def __getstate__(self):
#         """pickle state retrieval function, its most important use is to
#         delete the copied uuid to prevent potential issues from improper
#         restoration

#         Note:
#             If you overload this function, it's imperative that you call this
#             function via super().__getstate__(state), or otherwise return
#             a state dictionary without a uuid
#         """
#         state = self.__dict__.copy()
#         del state['uuid']
#         return state

#     def __setstate__(self, state):
#         """pickle restoration function, its most important use is to generate
#         a new uuid for the copied or deserialized object

#         Note:
#             If you overload this function, it's imperative that you call this
#             function via super().__setstate__(state), or otherwise create a
#             new unique uuid for the restored Pipeline _self.uuid = uuid4().hex
#         """
#         self.__dict__.update(state)
#         # create a new uuid for this instance, since it's technically a
#         # different object
#         self.uuid = uuid4().hex
#         # update the name to correspond with the new uuid
#         logger_name = self.__get_logger_name(self.name,
#                                                 self.sibling_id,
#                                                 self.uuid)
#         self.logger = get_logger(logger_name)



#     @staticmethod
#     def __get_logger_name(basename, sibling_id, uuid):
#         """generates a unique logger name that contains both a sibling id
#         (a random string that will be persistent across all copies and unpickled
#         versions of this object) and a uuid (which is unique to this exact
#         object instance)
#         (only the last six chars of each hash is used, so it's technically possible
#         for this name to not be unique) - if you need a truly unique ID, then
#         use obj.uuid
#         """
#         return "{basename} #{sibling_id}-{uuid}".format(basename=basename,
#                                                 sibling_id=sibling_id[-5:],
#                                                 uuid=uuid[-5:])
