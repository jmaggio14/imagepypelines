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
        self.keyword_inputs = []
        self.inputs = {}
        self.update(tasks)


    def update(self, tasks={}):
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

            self.vars[var] = {'block_node_id':None, # will always be defined
                                'block':None # will always be defined
                                }

        def _add_input(inpt, outputs, node_uuid):
            # track what inputs are required so we can populate
            # them with arguments in self.process
            if len(outputs) != 1:
                msg = "Inputs must define exactly one output"
                self.logger.error(msg)
                raise RuntimeError(msg)

            # add the input block to a tracking dictionary
            self.inputs[outputs[0]] = inpt

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
        for outputs,task in tasks.items():
            # make a single value into a list to simplify code
            if not isinstance(outputs, (tuple,list)):
                outputs = (outputs,)
            if not isinstance(task, (tuple,list)):
                task = (task,)

            # e.g. - 'z': (block, 'x', 'y'),
            if isinstance(task, (tuple,list)):
                block = task[0]
                args = task[1:]
                node_uuid = block.name + uuid4().hex + '-node'
                # if we have a tuple input, then the first value MUST be a block
                if not isinstance(block, Block):
                    raise TypeError("first value in any graph definition tuple must be a Block")

                # check if this block is an "Input" Block - this is a special case
                # e.g. - 'x': (ip.Input(),)
                if isinstance(block, Input):
                    _add_input(block, outputs, node_uuid)
                    if len(args) != 0:
                        raise RuntimeError("Input blocks cannot take any arguments")

                for output in outputs:
                    self.vars[output]['block_node_id'] = node_uuid
                    self.vars[output]['block'] = block

                # add the task to the graph
                self.graph.add_node(node_uuid,
                                    block=block,
                                    args=args,
                                    outputs=outputs,
                                    **block.get_default_node_attrs(),
                                    )

            else: # something other than a block or of tuple (block, var1, var2,...)
                raise RuntimeError("invalid task definition, must be block or tuple: (block, 'var1', 'var2',...)")

        ########################################################################
        #             Draw any new edges required for all block nodes
        ########################################################################
        # THIRD FOR LOOP - drawing edges
        for node_b,node_b_attrs in self.graph.nodes(data=True):
            # draw an edge for every input into this node
            for in_index, arg_name in enumerate(node_b_attrs['args']):
                # first we identify an upstream node by looking up what task
                # created them
                node_a = self.vars[arg_name]['block_node_id']
                node_a_attrs = self.graph.nodes[ node_a ]

                # draw the edge FOR THIS INPUT from node_a to node_b
                block_arg_name = node_b_attrs['block'].args[in_index]
                out_index = node_a_attrs['outputs'].index(arg_name)

                # edge key is {var_name}:{out_index}-->{in_index}
                edge_key = "{}:{}-->{}".format(arg_name, out_index, in_index)

                # draw the edge if it doesn't already exist
                if not self.graph.has_edge(node_a,node_b,edge_key):
                    self.graph.add_edge(node_a,
                                        node_b,
                                        # key
                                        key=edge_key,
                                        # attributes
                                        var_name = arg_name, # name assigned in graph definition
                                        out_index = out_index,
                                        in_index = in_index,
                                        name = block_arg_name, # name of node_b's process argument at the index
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
            elif isinstance(attrs['block'],Leaf):
                    continue
            else:
                end_nodes.append( (node,attrs) )

        for node,node_attrs in end_nodes:
            # this is a final node of the pipeline, so we need to draw a
            # leaf for each of its output edges
            for i,end_name in enumerate(node_attrs['outputs']):
                # add the leaf
                leaf = Leaf(end_name)
                leaf_uuid = leaf.name + uuid4().hex + '-node'
                self.graph.add_node(leaf_uuid,
                                    block=leaf,
                                    args=(end_name,),
                                    outputs=(end_name,),
                                    **leaf.get_default_node_attrs()
                                    )

                # edge key is {var_name}:{out_index}-->{in_index}
                edge_key = "{}:{}-->{}".format(end_name, i, 0)
                # draw the edge to the leaf
                # no need to check if it exists, because we just created the Leaf
                self.graph.add_edge(node,
                                    leaf_uuid,
                                    var_name=end_name, # name assigned in graph definition
                                    out_index=i,
                                    in_index=0,
                                    name=end_name, # name of node_b's process argument at the index
                                    data=None)



        ########################################################################
        #                   create input list & requirements
        ########################################################################
        # reset old index tracking lists
        self.indexed_inputs = []
        self.keyword_inputs = []
        # sort the inputs into keyword and indexed
        for inpt_name, inpt in self.inputs.items():
            # check if the input index is defined
            if isinstance(inpt.index,int):
                self.indexed_inputs.append(inpt_name)
            else:
                self.keyword_inputs.append(inpt_name)

        # sort the positonal inputs by index
        self.indexed_inputs.sort(key=lambda x: self.inputs[x].index)
        # sort keyword only inputs alphabetically
        self.keyword_inputs.sort()


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

        # log the current pipeline status
        self.logger.info("{} defined with inputs {}".format(self.name, self.args))






    def _compute(self):
        for node_a, node_b, edge_idx in self.execution_order:
            # get actual objects instead of just graph ids
            block_a = self.graph.nodes[node_a]['block']
            block_b = self.graph.nodes[node_b]['block']
            edge = self.graph.edges[node_a, node_b, edge_idx]

            # check if node_a is a root node (no incoming edges)
            # these nodes can be computed and the edge populated
            # immmediately because they have no predecessors
            # NOTE: this will currently break if a root has more than one
            # output - JM
            if self.graph.in_degree(node_a) == 0:
                # no arg data is needed
                edge['data'] = Data( block_a._pipeline_process(logger=self.logger)[0] )

            # compute this node if all the data is queued
            in_edges = self.graph.in_edges(node_b,data=True)
            if all((e[2]['data'] is not None) for e in in_edges):
                # fetch input data for this node
                in_edges = [e[2] for e in self.graph.in_edges(node_b, data=True)]
                arg_data_dict = {e['in_index'] : e['data'] for e in in_edges}
                args = [arg_data_dict[k] for k in sorted( arg_data_dict.keys() )]

                # assign the task outputs to their appropriate edge
                outputs = block_b._pipeline_process(*args, logger=self.logger)

                # populate upstream edges with the data we need
                # get the output names
                out_edges = [e[2] for e in self.graph.out_edges(node_b, data=True)]
                # URGENT!
                # NOTE: this won't work in all cases!
                # multiple edges can be connected to one out_index!
                out_edges_sorted = {e['out_index'] : e for e in out_edges}
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
        all_inputs = self.args
        # store positonal arguments fed in
        ## NOTE: need error checking here (number of inputs, etc)
        for i,data in enumerate(pos_data):
            inpt = self.inputs[ all_inputs[i] ]
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
            arg_vars = tuple(attrs['args'])
            out_vars = tuple(attrs['outputs'])
            block = attrs['block']

            # ignore leaf blocks
            if isinstance(block, Leaf):
                continue

            static[out_vars] = (block,) + arg_vars

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

        _get_priors(self.vars[var]['block_node_id'])

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

        _get_latters(self.vars[var]['block_node_id'])

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

    @property
    def args(self):
        return self.indexed_inputs + self.keyword_inputs











# END
