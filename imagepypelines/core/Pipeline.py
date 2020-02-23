# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018-2019 Jeff Maggio, Nathan Dileas, Ryan Hartzell
from ..Logger import get_logger
from .BaseBlock import BaseBlock
from .block_subclasses import SimpleBlock, BatchBlock, Input, Leaf

import inspect
import numpy as np
from uuid import uuid4
import networkx as nx
import matplotlib.pyplot as plt

class Pipeline(object):
    def __init__(self,
                    graph={},
                    name=None):
        # setup absolutely unique id for this block
        # this will change even if the block is copied or pickled
        self.uuid = uuid4().hex
        # ----------- building a unique name for this block ------------
        # name is set up as follows
        # <readable_name>-<sibling_id>-<uuid>
        if name is None:
            name = self.__class__.__name__

        self.name = name
        self.logger_name = self.__get_logger_name(name, self.uuid)
        self.logger = get_logger(self.logger_name)

        # GRAPHING
        self.graph = nx.MultiDiGraph()
        self.vars = {}

        # PROCESS / internal tracking
        self.inputs = {}
        self.data_dict = {}

        self._build_graph(user_graph=graph)


    def _build_graph(self,user_graph):
        # add all variables defined in the graph to a dictionary
        # quick helper function to add a node to the graph
        def _add_to_vars(var):
            if not isinstance(var,str):
                raise TypeError("graph vars must be a string")

            self.vars[var] = {'dependents':set(),
                                'task':None, # will always be defined
                                }


        #### FIRST FOR LOOP - defining the variables that we'll be using
        for var in user_graph.keys():
            # for str defined dict keys like 'x' : (func, 'a', 'b')
            if isinstance(var, str):
                _add_to_vars(var)

            # for tuple defined dict keys like ('x','y') : (func, 'a', 'b')
            elif isinstance(var,(tuple,list)):
                for v in var:
                    _add_to_vars(v)


        #### SECOND FOR LOOP - adding all nodes to the graph
        # reiterate through the graph definition to define inputs and outputs
        for outputs,definition in user_graph.items():
            # make a single value into a list to simplify code
            if not isinstance(outputs, (tuple,list)):
                outputs = [outputs]

            # GETTING GRAPH INPUTS
            # e.g. - 'x': ip.Input(),
            if isinstance(definition, Input):
                # track what inputs are required so we can populate
                # them with arguments in self.process
                self.inputs[definition.index_key] = definition

                # add this variables task to it's attrs
                # these vars will not have any dependents
                for output in outputs:
                    self.vars[output]['task'] = definition.uuid

                # add the input 'task' to the graph
                # inputs will not have any inputs (ironically) or a task_processor
                # as these inputs are just placeholders for data supplied by the user
                self.graph.add_node(definition.uuid,
                                    task_processor=definition,
                                    inputs=tuple(),
                                    outputs=outputs,
                                    **definition.get_default_node_attrs(),)



            # e.g. - 'z': (block, 'x', 'y'),
            elif isinstance(definition, (tuple,list)):
                task = definition[0]
                inpts = definition[1:]
                # if we have a tuple input, then the first value MUST be a block or Pipeline
                if not isinstance(task, (BaseBlock,Pipeline)):
                    raise TypeError(
                        "first value in any graph definition tuple must be a Block or Pipeline")

                for output in outputs:
                    self.vars[output]['task'] = task.uuid

                # add the task to the graph
                # import pdb; pdb.set_trace()
                self.graph.add_node(task.uuid,
                                    task_processor=task,
                                    inputs=inpts,
                                    outputs=outputs,
                                    **task.get_default_node_attrs(),
                                    )

                # update the dependents for all of these outputs
                for output in outputs:
                    self.vars[output]['dependents'].update(inpts)




        # THIRD FOR LOOP - drawing edges
        for node_b,node_b_attrs in self.graph.nodes(data=True):
            # draw an edge for every input into this node
            for input_index, input_name in enumerate(node_b_attrs['inputs']):
                # first we identify an upstream node by looking up what task
                # created them
                node_a = self.vars[input_name]['task']
                node_a_attrs = self.graph.nodes[ node_a ]

                # draw the edge FOR THIS INPUT from node_a to node_b
                processor_arg_name = node_b_attrs['task_processor'].inputs[input_index]
                self.graph.add_edge(node_a,
                                    node_b,
                                    var_name=input_name, # name assigned in graph definition
                                    input_index=input_index,
                                    output_index=node_a_attrs['outputs'].index(input_name),
                                    name=processor_arg_name, # name of node_b's process argument at the index
                                    data=None) # none is a placeholder value. it will be populated
                print("drawing edge {} from {} to {}".format(input_index,
                                                                node_a,
                                                                node_b))


        # FOURTH FOR LOOP - drawing leaf nodes
        # this is required so we can store data on end edges - otherwise the final
        # nodes of our pipeline won't have output edges, so we can't store data
        # on those edges
        end_nodes = [(node,attrs) for node,attrs in self.graph.nodes(data=True) if (self.graph.out_degree(node) ==  0)]

        for node,node_attrs in end_nodes:
            # this is a final node of the pipeline, so we need to draw a
            # leaf for each of its output edges
            for i,end_name in enumerate(node_attrs['outputs']):
                # add the leaf
                leaf = Leaf(end_name)
                self.graph.add_node(leaf.uuid,
                                    task_processor=leaf,
                                    inputs=(end_name,),
                                    outputs=(end_name,),
                                    **leaf.get_default_node_attrs()
                                    )

                # draw the edge to the leaf
                self.graph.add_edge(node,
                                    leaf.uuid,
                                    var_name=end_name, # name assigned in graph definition
                                    input_index=0,
                                    output_index=i,
                                    name=end_name, # name of node_b's process argument at the index
                                    data=None)

    @property
    def execution_order(self):
        return nx.topological_sort( nx.line_graph(self.graph) )

    def _compute(self):
        n_edges_loaded = 0
        for node_a, node_b, edge_idx in self.execution_order:
            n_edges_loaded += 1
            # get actual objects instead of just graph ids
            task_a = self.graph.nodes[node_a]['task_processor']
            task_b = self.graph.nodes[node_b]['task_processor']
            edge = self.graph.edges[node_a, node_b, edge_idx]

            # check if node_a is a root node (no incoming edges)
            # these nodes can be computed and the edge populated
            # immmediately because they have no dependents
            if self.graph.in_degree(node_a) == 0:
                edge['data'] = task_a._pipeline_process() # no data needed

            # check if all the data for this node is loaded
            # inputs (and other roots) will have zero required edges

            n_edges_required = self.graph.in_degree(node_b)
            if n_edges_loaded == n_edges_required:

                # fetch input data for this node
                in_edges = [e[2] for e in self.graph.in_edges(node_b, data=True)]
                input_data_dict = {e['input_index'] : e['data'] for e in in_edges}
                inputs = [input_data_dict[k] for k in sorted( input_data_dict.keys() )]

                # assign the task outputs to their appropriate edge
                outputs = task_b._pipeline_process(*inputs)

                # populate upstream edges with the data we need
                # get the output names
                out_edges = [e[2] for e in self.graph.out_edges(node_b, data=True)]
                out_edges_sorted = {e['output_index'] : e for e in out_edges}
                out_edges_sorted = [out_edges_sorted[k] for k in sorted(out_edges_sorted.keys())]
                # NEED ERROR CHECKING HERE
                # (psuedo) if n_out == n_expected_out
                for i,out_edge in enumerate(out_edges_sorted):
                    out_edge['data'] = outputs[i]

                n_edges_loaded = 0


    def process(self,*pos_data,**kwdata):
        # reset all leftover data in this graph
        self.clear()

        # STORING DATA
        # store positonal arguments fed in
        ## NOTE: need error checking here (number of inputs, etc)
        for i,data in enumerate(pos_data):
            self.inputs[i].load(data)

        # store keyword arguments fed in
        ## NOTE: need error checking here (number of inputs, etc)
        for key,val in kwdata.items():
            self.inputs[key].load(val)

        # PROCESS
        self._compute()

        return {edge['var_name'] : edge['data'] for _,_,edge in self.graph.edges(data=True)}


    def clear(self):
        """resets all data temporarily stored in the graph"""
        for var in self.vars.values():
            var['data'] = None

    def draw(self):
        plt.cla()
        nx.draw_networkx(self.graph,
                            pos=nx.planar_layout(self.graph),
                            labels= { n : self.graph.nodes[n]['name'] for n in self.graph.nodes()},
                            node_color='orange' )
        plt.ion()
        plt.draw()
        plt.show()
        plt.pause(0.01)


    ################################### util ###################################
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
        return state

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
        # update the name to correspond with the new uuid
        logger_name = self.__get_logger_name(self.name,
                                                self.sibling_id,
                                                self.uuid)
        self.logger = get_logger(logger_name)



    @staticmethod
    def __get_logger_name(basename, uuid):
        """generates a unique logger name that contains both a sibling id
        (a random string that will be persistent across all copies and unpickled
        versions of this object) and a uuid (which is unique to this exact
        object instance)
        (only the last six chars of each hash is used, so it's technically possible
        for this name to not be unique) - if you need a truly unique ID, then
        use obj.uuid
        """
        return "{0} #{1}".format(basename, uuid[-6:])
