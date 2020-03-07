# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018-2020 Jeff Maggio, Nathan Dileas, Ryan Hartzell
from ..Logger import get_logger
from .Block import Block
from .Data import Data
from .block_subclasses import Block, Input, Leaf
from .constants import UUID_ORDER

import inspect
import numpy as np
from uuid import uuid4
import networkx as nx
import pickle
import base64
import json

class Pipeline(object):
    """processing pipeline manager for simple algorithm construction

    The Pipeline is t


    Attributes:
        uuid(str): hex uuid for this pipeline
        name(str): user specified name for this pipeline, used to generate
            the logger_name. defaults to "Pipeline" or the name of your subclass
        logger_name(str): unique name for this pipeline's logger. Generated from
            a combination of name and uuid
        logger(:obj:`ip.ImagepypelinesLogger`): Logger object for this pipeline

    """
    def __init__(self, tasks={}, name=None):
        """initializes the pipeline with a user-provided graph (tasks)

        Args:
            tasks (dict): graph definition to construct this pipeline
            name (str): name used to generate the logger name

        """
        # setup absolutely unique id for this block
        # this will change even if the block is copied or pickled
        self.uuid = uuid4().hex # unique univeral hex ID for this pipeline
        # ----------- building a unique name for this block ------------
        # name is set up as follows
        # <readable_name>-<sibling_id>-<uuid>
        if name is None:
            name = self.__class__.__name__
        self.name = name # string name - used to generate the logger_name

        # build the logger for this pipeline
        self.logger = get_logger( self.id )

        # GRAPHING
        self.graph = nx.MultiDiGraph()
        self.vars = {}

        # PROCESS / internal tracking
        self.indexed_inputs = []
        self.kwonly_inputs = []
        self.inputs = {}
        self.update(tasks)


    def update(self, task={}):
        ########################################################################
        #                           HELPER FUNCTIONS
        ########################################################################
        def _add_to_vars(var):
            if not isinstance(var,str):
                msg = "graph vars must be a string, not %s" % type(var)
                self.logger.error(msg)
                raise TypeError(msg)

            if var in self.vars.keys():
                msg = "\"%s\" cannot be defined more than once" % var
                self.logger.error(msg)
                raise TypeError(msg)

            self.vars[var] = {'task_id':None, # will always be defined
                                'task_processor':None # will always be defined
                                }

        def _add_input(inpt, node_uuid):
            # track what inputs are required so we can populate
            # them with arguments in self.process
            if len(outputs) != 1:
                msg = "Inputs must define exactly one output"
                self.logger.error(msg)
                raise RuntimeError(msg)

            # add the input block to a tracking dictionary
            self.inputs[outputs[0]] = node_uuid

        # ======================================================================
        #                           GRAPH CONSTRUCTION
        # ======================================================================



        ########################################################################
        #           Define the variables we'll be using for these tasks
        ########################################################################
        # add all variables defined in the graph to a dictionary
        for var in tasks.keys():
            # for str defined dict keys like 'x' : (func, 'a', 'b')
            if isinstance(var, str):
                _add_to_vars(var)

            # for tuple defined dict keys like ('x','y') : (func, 'a', 'b')
            elif isinstance(var,(tuple,list)):
                for v in var:
                    _add_to_vars(v)


        ########################################################################
        #                    Add all the task nodes to the graph
        ########################################################################
        # reiterate through the graph definition to define inputs and outputs
        for outputs,definition in tasks.items():
            # make a single value into a list to simplify code
            if not isinstance(outputs, (tuple,list)):
                outputs = [outputs]

            # GETTING GRAPH INPUTS
            if isinstance(definition, Block):
                node_uuid = definition.name + uuid4().hex + '-node'
                # check if we are dealing with an input
                # e.g. - 'x': ip.Input(),
                # otherwise we are dealing with a block with no inputs
                if isinstance(definition, Input):
                    _add_input(definition, node_uuid)

                # add this variables task to it's attrs
                # these vars will not have any predecessors
                for output in outputs:
                    self.vars[output]['task_id'] = node_uuid
                    self.vars[output]['task_processor'] = definition

                # add the input 'task' to the graph
                # inputs will not have any inputs (ironically)
                # as these inputs are psuedo-blocks for data supplied by the user
                self.graph.add_node(node_uuid,
                                    task_processor=definition,
                                    inputs=tuple(),
                                    outputs=outputs,
                                    **definition.get_default_node_attrs(),)



            # e.g. - 'z': (block, 'x', 'y'),
            elif isinstance(definition, (tuple,list)):
                task = definition[0]
                args = definition[1:]
                node_uuid = task.name + uuid4().hex + '-node'
                # if we have a tuple input, then the first value MUST be a task
                if not isinstance(task, Block):
                    raise TypeError("first value in any graph definition tuple must be a Block")

                # check if this task is an "Input" Block - this is a special case
                # e.g. - 'x': (ip.Input(),)
                if isinstance(task, Input):
                    _add_input(task, node_uuid)
                    if len(args) != 0:
                        raise RuntimeError("Input blocks cannot take any arguments")

                for output in outputs:
                    self.vars[output]['task_id'] = node_uuid
                    self.vars[output]['task_processor'] = task

                # add the task to the graph
                self.graph.add_node(node_uuid,
                                    task_processor=task,
                                    inputs=args,
                                    outputs=outputs,
                                    **task.get_default_node_attrs(),
                                    )

            else: # something other than a block or of tuple (block, var1, var2,...)
                raise RuntimeError("invalid task definition, must be block or tuple: (block, 'var1', 'var2',...)")

        ########################################################################
        #             Draw any new edges required for all task nodes
        ########################################################################
        # THIRD FOR LOOP - drawing edges
        for node_b,node_b_attrs in self.graph.nodes(data=True):
            # draw an edge for every input into this node
            for input_index, input_name in enumerate(node_b_attrs['inputs']):
                # first we identify an upstream node by looking up what task
                # created them
                node_a = self.vars[input_name]['task_id']
                node_a_attrs = self.graph.nodes[ node_a ]

                # draw the edge FOR THIS INPUT from node_a to node_b
                processor_arg_name = node_b_attrs['task_processor'].inputs[input_index]
                output_index = node_a_attrs['outputs'].index(input_name)

                # edge key is {var_name}:{output_index}-->{input_index}
                edge_key = "{}:{}-->{}".format(var_name, output_index, input_index)

                # draw the edge if it doesn't already exist
                if not self.graph.has_edge(node_a,node_b,edge_key):
                    self.graph.add_edge(node_a,
                                        node_b,
                                        # key
                                        key=edge_key,
                                        # attributes
                                        var_name = input_name, # name assigned in graph definition
                                        input_index = input_index,
                                        output_index = output_index,
                                        name = processor_arg_name, # name of node_b's process argument at the index
                                        data = None, # none is a placeholder value. it will be populated
                                        )


        ########################################################################
        #             Draw 'leaves' on tasks with no output edges
        #             this is required so they will still be computable
        ########################################################################
        # this is required so we can store data on end edges - otherwise the final
        # nodes of our pipeline won't have output edges, so we can't store data
        # on those edges

        # make a list of nodes without outgoing edges
        end_nodes = []
        for node,attrs in self.graph.nodes(data=True):
            # if the node already has outputs, we don't need a leaf out of it
            if self.graph.out_degree(node) > 0:
                continue
            # if the end node is a Leaf already, then we don't need another leaf
            elif isinstance(attrs['task_processor'],Leaf):
                continue
            else:
                end_nodes.append(node)

        for node,node_attrs in end_nodes:
            # this is a final node of the pipeline, so we need to draw a
            # leaf for each of its output edges
            for i,end_name in enumerate(node_attrs['outputs']):
                # add the leaf
                leaf = Leaf(end_name)
                leaf_uuid = leaf.name + uuid4().hex + '-node'
                self.graph.add_node(leaf_uuid,
                                    task_processor=leaf,
                                    inputs=(end_name,),
                                    outputs=(end_name,),
                                    **leaf.get_default_node_attrs()
                                    )

                # edge key is {var_name}:{output_index}-->{input_index}
                edge_key = "{}:{}-->{}".format(end_name, i, 0)
                # draw the edge to the leaf
                # no need to check if it exists, because we just created the Leaf
                self.graph.add_edge(node,
                                    leaf_uuid,
                                    var_name=end_name, # name assigned in graph definition
                                    input_index=0,
                                    output_index=i,
                                    name=end_name, # name of node_b's process argument at the index
                                    data=None)



        ########################################################################
        #                   create input list & requirements
        ########################################################################
        # reset old index tracking lists
        self.indexed_inputs = []
        self.kwonly_inputs = []
        # fetch all the input objects in the graph
        all_inputs = [self.graph.nodes[node_id]['task_processor'] for node_id in self.inputs]
        # sort the inputs into kwonly and indexed
        for inpt in all_inputs:
            # check if the input index is defined
            if inpt.index:
                self.indexed_inputs.append(inpt)
            else:
                self.kwonly_inputs.append(inpt)

        # sort the positonal inputs by index
        self.indexed_inputs.sort(key=lambda x: self.inputs[x].index)
        # sort keyword only inputs alphabetically
        self.kwonly_inputs.sort()


        # check to make sure an input index isn't defined twice
        indices_used = [self.inputs[x].index for x in self.indexed_inputs]
        if len(set(indices_used)) != len(indices_used):
            # Note: add more verbose error message
            msg = "Input indices cannot be reused"
            self.logger.error(msg)
            raise RuntimeError(msg)

        # check to make sure input indexes are consecutive (don't skip)
        if max(indices_used) + 1 != len(indices_used):
            # Note: add more verbose error message
            msg = "Input indices must be consecutive"
            self.logger.error(msg)
            raise RuntimeError(msg)


        self.logger.info("{} defined with inputs {}".format(self.name, self.indexed_inputs + self.kwonly_inputs))

    def _compute(self):
        for node_a, node_b, edge_idx in self.execution_order:
            # get actual objects instead of just graph ids
            task_a = self.graph.nodes[node_a]['task_processor']
            task_b = self.graph.nodes[node_b]['task_processor']
            edge = self.graph.edges[node_a, node_b, edge_idx]

            # check if node_a is a root node (no incoming edges)
            # these nodes can be computed and the edge populated
            # immmediately because they have no predecessors
            # NOTE: this will currently break if a root has more than one
            # output - JM
            if self.graph.in_degree(node_a) == 0:
                # no input data is needed
                edge['data'] = Data( task_a._pipeline_process(logger=self.logger)[0] )

            # compute this node if all the data is queued
            in_edges = self.graph.in_edges(node_b,data=True)
            if all((e[2]['data'] is not None) for e in in_edges):
                # fetch input data for this node
                in_edges = [e[2] for e in self.graph.in_edges(node_b, data=True)]
                input_data_dict = {e['input_index'] : e['data'] for e in in_edges}
                inputs = [input_data_dict[k] for k in sorted( input_data_dict.keys() )]

                # assign the task outputs to their appropriate edge
                outputs = task_b._pipeline_process(*inputs, logger=self.logger)

                # populate upstream edges with the data we need
                # get the output names
                out_edges = [e[2] for e in self.graph.out_edges(node_b, data=True)]
                # URGENT!
                # NOTE: this won't work in all cases!
                # multiple edges can be connected to one output_index!
                out_edges_sorted = {e['output_index'] : e for e in out_edges}
                out_edges_sorted = [out_edges_sorted[k] for k in sorted(out_edges_sorted.keys())]
                # NEED ERROR CHECKING HERE
                # (psuedo) if n_out == n_expected_out
                for i,out_edge in enumerate(out_edges_sorted):
                    out_edge['data'] = Data(outputs[i])


    def process(self,*pos_data,**kwdata):
        # reset all leftover data in this graph
        self.clear()

        # --------------------------------------------------------------
        # STORING INPUTS - inside the input nodes
        # --------------------------------------------------------------
        # store positonal arguments fed in
        ## NOTE: need error checking here (number of inputs, etc)
        for i,data in enumerate(pos_data):
            inpt = self.inputs[ self.indexed_inputs[i] ]
            # check if the data has already been loaded
            if inpt.loaded:
                self.logger.error(self.indexed_inputs[i] + " has already been loaded")
                raise RuntimeError()
            inpt.load(data)

        # store keyword arguments fed in
        ## NOTE: need error checking here (number of inputs, etc)
        for key, val in kwdata.items():
            inpt = self.inputs[key]
            # check if the data has already been loaded
            if inpt.loaded:
                self.logger.error(key + " has already been loaded")
                raise RuntimeError()
            inpt.load(val)

        # check to make sure all inputs are loaded
        data_loaded = True
        for key,inpt in self.inputs.items():
            if not inpt.loaded:
                msg = "data for \"%s\" must be provided" % key
                self.logger.error(msg)
                data_loaded = False

        if not data_loaded:
            raise RuntimeError("insufficient input data provided")

        # --------------------------------------------------------------
        # PROCESS
        # --------------------------------------------------------------
        self._compute()

        return {edge['var_name'] : edge['data'].pop() for _,_,edge in self.graph.edges(data=True)}

    def clear(self):
        """resets all edges in the graph, clears the inputs"""
        for _,_,edge in self.graph.edges(data=True):
            edge['data'] = None

        for inpt in self.inputs.values():
            inpt.unload()

    def draw(self, show=True, ax=None):
        # visualize(self, show, ax)
        pass

    ################################### util ###################################
    def get_static_representation(self):
        """generates a dictionary represenation of the pipeline, which can be
        used to make other pipelines.
        """
        static = {}
        for _,attrs in self.graph.nodes(data=True):
            input_vars = tuple(attrs['inputs'])
            output_vars = tuple(attrs['outputs'])
            task_processor = attrs['task_processor']

            # ignore leaf blocks
            if isinstance(task_processor, Leaf):
                continue

            static[output_vars] = (task_processor,) + input_vars

        return static


    def debug_pickle(self, pickle_protocol=pickle.HIGHEST_PROTOCOL):
        """helper function to debug what part of a block is not serializable"""
        error = False

        # fetch the static graph represenation
        static = self.get_static_representation()

        # rebuild the static graph with pickled blocks
        raise_error = False
        pickled_static = {}
        for outputs,task in static.items():
            block = task[0]
            # iterate through every value in the block's __dict__
            for key,val in block.__dict__.items():
                try:
                    pickle.dumps(val, protocol=pickle_protocol)
                except Exception as e:
                    self.logger.error("error pickling {}.{}: {}".format(block,key,e))
                    error = True

        if not error:
            self.logger.info("no pickling issues detected")


    def get_predecessors(self, var):
        # NOTE: we could possibly speed this function up by using a depth
        # finding algorithm instead?
        # define a recursive function to get edges from all predecessor nodes
        preds = set()
        nodes_checked = []
        def _get_priors(node):
            for node_a,node_b,var_name in self.graph.in_edges(node,'var_name'):
                preds.add(var_name)
                # recursively add edges from the source node
                if node_a not in nodes_checked:
                    _get_priors(node_a)

            nodes_checked.append(node)

        _get_priors(self.vars[var]['task_id'])

        return preds

    def get_successors(self, var):
        # NOTE: we could possibly speed this function up by using a depth
        # finding algorithm instead?
        # define a recursive function to get edges from all successor nodes
        succs = set()
        nodes_checked = []
        def _get_latters(node):
            for node_a,node_b,var_name in self.graph.out_edges(node,'var_name'):
                succs.add(var_name)
                # recursively add edges from the source node
                if node_b not in nodes_checked:
                    _get_latters(node_b)

            nodes_checked.append(node)

        _get_latters(self.vars[var]['task_id'])

        # remove the name of the variable
        succs.remove(var)
        return succs

    def assign_input_index(self, var, index):
        # reset the input index to a new one
        self.inputs[var].set_index(index)
        self.update()


    ################################ properties ################################
    @property
    def id(self):
        return "{}#{}".format(self.name,self.uuid[-UUID_ORDER:])

    @property
    def execution_order(self):
        return nx.topological_sort( nx.line_graph(self.graph) )







# END
