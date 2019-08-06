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
from .block_subclasses import SimpleBlock, BatchBlock
from .Exceptions import CrackedPipeline
from .Exceptions import IncompatibleTypes
from .util import Timer

import collections
import pickle
import copy
import numpy as np
from termcolor import cprint
from uuid import uuid4


class FuncBlock(SimpleBlock):
    def __init__(self,func,preset_kwargs):
        self.func = func
        self.preset_kwargs = preset_kwargs

        # check if the function meets requirements
        spec = inspect.getfullargspec(func)

        # we can't allow varargs at all because a block must have a known
        # number of inputs
        if not (spec.varargs or spec.varkw):
            raise TypeError("function cannot accept a variable number of args")

        num_required = len(spec.args) - len(preset_kwargs)
        self.required = spec.args[:num_required]

        eval_string = \
        """
        def process(self,{required}):
            return self.func({required},**self.preset_kwargs)
        """.format(required = ', '.join(self.required))

        self.process = eval(eval_string)
        super().__init__()


    def __call__(self,*args,**kwargs):
        """returns the exact output of the user defined function without any
        interference or interaction with the class
        """
        return self.func(*args,**kwargs)


def blockify(**kwargs):
    def decorator(func):
        def _blockify():
            return FuncBlock(func,kwargs)
        return _blockify
    return decorator



class PlaceHolder(BatchBlock):
    def __init__(self):
        self.data = None
        super().__init__()

    def load(self,data):
        self.datas = data

    def batch_process(self,input_=None):
        return self.data




# dsk = {
#     "load-1": {load: "myfile.cfg", analyze: "something"},
#     "load-2":
#         {
#         "input":{blank dict b/c no input},
#         "output":{load: "myfile.cfg", analyze: "something"}
#         },
#     "clean-1":
#         {
#         "input":{load: "myfile.cfg", analyze: "something"},
#         "output":{other_func: "yeet"}
#         },
#     "clean-2": {load: "myfile.cfg", analyze: "something"},
#     }



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
        self.graph = nx.MultiDiGraph()

        self.vars = {}

        self.data_dict = {}

        if isinstance(graph, dict):
            # EXAMPLE FOR DEBUG
            dsk = {'x': ip.PlaceHolder(),
                    'y':ip.PlaceHolder(),
                    ('z1','z2'): (add, 'x', 'y'),
                    'w': (sum, ['x', 'y', 'z'])}


            # add all nodes to the graph first
            # quick helper function to add a node to the graph
            def _add_to_vars(var):
                if not isinstance(var,str):
                    raise TypeError("graph vars must be a string")

                self.vars[var] = {'dependents':set(),
                                    'processor':None}

            for var in dsk.keys():
                # for str defined dict keys like 'x' : (func, 'a', 'b')
                if isinstance(var, str):
                    _add_to_vars(var)

                # for tuple defined dict keys like ('x','y') : (func, 'a', 'b')
                elif isinstance(var,(tuple,list)):
                    for n in var:
                        _add_to_vars(var)

            # reiterate through the graph definition to define inputs and outputs
            for var,definition in dsk.items():
                # e.g. - 'x': ip.PlaceHolder(),
                if isinstance(definition, ip.PlaceHolder):
                    # add this variables processor to it's attrs
                    # these vars will not have any dependents
                    self.vars[var]['processor'] = definition.uuid

                    # add the processor to the graph
                    self.graph.add_node(definition.uuid,
                                        definition.get_default_node_attrs())

                # e.g. - 'z': (block, 'x', 'y'),
                elif isinstance(definition,(tuple,list)):
                    processor = definition[0]
                    inpts = definition[1:]
                    # if we have a tuple input, then the first value MUST be a block or Pipeline
                    if not isinstance(processor, (BaseBlock,Pipeline)):
                        raise TypeError(
                            "first value in any graph definition tuple must be a Block or Pipeline")


                    # add the processor to the graph
                    self.graph.add_node(processor.uuid,
                                        processor.get_default_node_attrs(),
                                        processor=processor,
                                        inputs=inpts)

                    # now we iterate through the inputs and draw edges between nodes
                    self.vars[var][dependents].update(inpts)









                else:
                    graph.nodes[node]['inputs'].append(inputs)

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
        for node in self.data.keys():
            self.graph.add_node


    def _get_topology(self):

        required_data = set()


        topological_order =
            tuple(nx.topological_sort(nx.line_graph(self.graph)))

        last_node = None
        data = {}
        # first node is always a pipeline_input for the first iteration
        for _, node_b, _ in topological_order:
            # iterate through the topological_order which contains
            if node_b == last_node:
                continue

            processor = node_b['uuid']
            incoming_data = node_b.in_edges()

            required_data =










        # iterate through processors and yield them
        # for node_a, node_b, edge_idx in uuid_order:
        #     processor_a = self.graph.nodes[node_a]['obj']
        #     processor_b = self.graph.nodes[node_b]['obj']
        #     yield processor_a, processor_b, edge_idx


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
