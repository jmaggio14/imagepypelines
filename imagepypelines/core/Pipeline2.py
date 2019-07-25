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


class Pipeline(object):
    def __init__(self,
                    graph=[],
                    name=None):

         # this uuid will not change with copying or serialization
         # as such it can be used to id which blocks are copies or unpickled
         # versions of the original - it's metaphorical siblings
        self.sibling_id = uuid4().hex
        # setup absolutely unique id for this block
        # this will change even if the block is copied or pickled
        self.uuid = uuid4().hex
        # ----------- building a unique name for this block ------------
        # name is set up as follows
        # <readable_name>-<sibling_id>-<uuid>
        if name is None:
            name = self.__class__.__name__

        self.name = name
        self.logger_name = self.__get_logger_name(name,
                                                self.sibling_id,
                                                self.uuid)
        self.logger = get_logger(self.logger_name)
        self.step_types = []

        if isinstance(graph, (list,tuple)):
            self.graph = nx.MultiDiGraph()
            self.graph.add_node( graph[0].uuid,
                                    graph[0].get_default_node_attrs() )

            for block_a,block_b in zip(graph,graph[1:]):
                self.graph.add_node(block_b.uuid,
                                        block_b.get_default_node_attrs() )

                # connect an edge for every input in block_b (block2)
                for i in range(block_b.n_inputs):
                    self.graph.add_edge(block_a.uuid,
                                        block_b.uuid,
                                        **block_b.get_input_edge_attrs(i))

        elif isinstance(graph,(nx.DiGraph, nx.MultiDiGraph)):
            # TODO:
            # make sure every element is a pipeline or graph
            # add node and edge attributes
            self.graph = graph

        else:
            raise TypeError(
                    "'graph' must be tuple, list, or directed networkx Graph")


        self.data = data

    def process(self, *data, **named_data):
        # JM: TODO
        # check to make sure all data is a list or row separable array

        # Save all data passed in to a dictionary with a unique identifier
        self.data = {'pipeline_input $%s' % i for i in range(len(data)) :
                        d for d in data}

        # check to make sure the 'named_data' dictionary contains already
        # existing keys, this is done by checking key intersection using the
        # '&' operator
        if len( self.data.keys() & named_data.keys() ) > 0:
            raise KeyError("illegal input variable name key")
        self.data.update(named_data)

        # JM: TODO
        # add logging to follow along with this
        # self.graph.add_nodes_from( self.data.keys() )






    def _get_topology(self):
        uuid_order = tuple( nx.topological_sort(nx.line_graph(self.graph)) )

        # iterate through processors and yield them
        for node_a, node_b, edge_idx in uuid_order:
            processor_a = self.graph.nodes[node_a]['obj']
            processor_b = self.graph.nodes[node_b]['obj']
            yield processor_a, processor_b, edge_idx


    def draw(self, display=True):
        """generates a matplotlib figure that graphically represents the
        graph for a human

        Args:
            display(bool): whether or not to display the graph, or just return
                the Figure

        Returns:
            matplotlib.pyplot.Figure: figure which represents the graph
        """
        # real code here:
        fig = plt.figure()
        axes = fig.add_subplot(111)

        # get positioning for nodes
        pos = nx.spring_layout(self.graph)

        nx.draw(self.graph,
                    pos,
                    with_labels=True,
                    font_weight='bold',
                    node_color='orange')
        if display:
            plt.show()

        return fig


    @property
    def inputs(self):
