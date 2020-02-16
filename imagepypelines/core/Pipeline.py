# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018-2019 Jeff Maggio, Nathan Dileas, Ryan Hartzell
from ..Logger import get_logger
from .BaseBlock import BaseBlock
from .block_subclasses import SimpleBlock, BatchBlock
from .util import Timer

import collections
import inspect
import pickle
import copy
import numpy as np
from termcolor import cprint
from uuid import uuid4
import networkx as nx
import matplotlib.pyplot as plt

def get_types(data):
    """Retrieves the block data type of the input datum"""
    def _get_types():
        for datum in data:
            if isinstance(datum,np.ndarray):
                yield (ArrayType(datum.shape),)
            else:
                yield (type(datum),)

    return set( _get_types() )

class FuncBlock(SimpleBlock):
    """Block that will run anmy fucntion you give it, either unfettered through
    the __call__ function, or with optional hardcoded parameters for use in a
    pipeline. Typically the FuncBlock is only used in the `blockify` decorator
    method.

    Args:
        func (function): the function you desire to turn into a block
        preset_kwargs (dict): preset keyword arguments, typically used for
            arguments that are not data to process
    """
    # def __new__(self, func, preset_kwargs):
    #     return type(func.__name__+"FuncBlock", (SimpleBlock,), {})

    def __init__(self,func, preset_kwargs):
        self.func = func
        self.preset_kwargs = preset_kwargs

        # check if the function meets requirements
        spec = inspect.getfullargspec(func)

        # we can't allow varargs at all because a block must have a known
        # number of inputs
        if (spec.varargs or spec.varkw):
            raise TypeError("function cannot accept a variable number of args")

        num_required = len(spec.args) - len(preset_kwargs)
        required = spec.args[:num_required]

        exec_string = \
        """def process(self,{required}): return self.func({required},**self.preset_kwargs)
        """.format(required = ', '.join(required))
        exec_locals = {}
        exec(exec_string, {}, exec_locals)
        self.process = exec_locals['process']
        super().__init__(self.func.__name__)

    def __call__(self,*args,**kwargs):
        """returns the exact output of the user defined function without any
        interference or interaction with the class
        """
        return self.func(*args,**kwargs)

    def __str__(self):
        return self.func.__name__+"FuncBlock"




def blockify(**kwargs):
    """decorator which converts a normal function into a un-trainable
    block which can be added to a pipeline. The function can still be used
    as normal after blockification (the __call__ method is setup such that
    unfettered access to the function is permitted)

    Example:
        >>> import imagepypelines as ip
        >>>
        >>> @ip.blockify(value=10)
        >>> def add_value(datum, value):
        ...    return datum + value
        >>>
        >>> type(add_value)
        <class 'FuncBlock'>

    Args:
        **kwargs: hardcode keyword arguments for a function, these arguments
            will not have to be used to

    """
    def decorator(func):
        def _blockify():
            return FuncBlock(func,kwargs)
        return _blockify
    return decorator


class Data(object):
    def __init__(self,data):
        self.data = data
        if isinstance(data, np.ndarray):
            self.type = "array"
        elif isinstance(data, (list,tuple)):
            self.type = "iter"
        else:
            self.type = "iter"
            self.data = [self.data]

    def batch_data(self):
        return self.data

    def datums(self):
        if self.type == "iter":
            for d in self.data:
                yield d

        elif self.type == "array":
            # return every row of data
            for r in range(self.data.shape[0]):
                yield self.data[r]


class Input(BatchBlock):
    def __init__(self,index_key=None):
        self.index_key = index_key
        # DEBUG
        # eventually we will be able to specify inputs using
        # END DEBUG
        self.data = None
        super().__init__(name="Input"+str(self.index_key))

    def batch_process(self):
        return self.data

    def load(self, data):
        self.data = data

    def unload(self, data):
        self.data = None



class Pipeline(object):
    def __init__(self,
                    graph={},
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
                node_a_attrs = self.graph.node[ node_a ]

                # draw the edge FOR THIS INPUT from node_a to node_b
                processor_arg_name = node_b_attrs['task_processor'].inputs[input_index]
                self.graph.add_edge(node_a,
                                    node_b,
                                    var_name=input_name, # name assigned in graph definition
                                    input_index=input_index,
                                    output_index=node_a_attrs['outputs'].index(input_name),
                                    name=processor_arg_name, # name of node_b's process argument at the index
                                    data=None)
                print("drawing edge {} from {} to {}".format(input_index,
                                                                node_a,
                                                                node_b))

    @property
    def execution_order(self):
        return nx.topological_sort( nx.line_graph(self.graph) )


    def _compute(self):
        n_edges_loaded = 0
        for node_a, node_b, edge_idx in self.execution_order:
            # get actual objects instead of just graph ids
            task_a = self.graph.nodes[node_a]['task_processor']
            task_b = self.graph.nodes[node_b]['task_processor']
            edge = self.graph.edges[node_a, node_b, edge_idx]

            # check if node_a is a root node (no incoming edges)
            # these nodes can be computed and the edge populated
            # immmediately because they have no dependents
            # if self.graph.in_degree(node_a) == 0:
            #     edge['data'] = task_a._pipeline_process() # no data needed

            # check if all the data for this node is loaded
            # inputs (and other roots) will have zero required edges

            n_edges_required = self.graph.in_degree(node_b)
            if n_edges_loaded == n_edges_required:

                # fetch input data for this node
                in_edges = [e[2] for e in self.graph.in_edges(node_b, data=True)]
                input_names_dict = {e['input_index'] : e['var_name'] for e in in_edges}
                inputs = sorted(input_names_dict, key=input_names_dict.get)

                # assign the task outputs to their appropriate edge
                outputs = task_b._pipeline_process(*inputs)

                # populate upstream edges with the data we need
                # get the output names
                out_edges = [e[2] for e in self.graph.out_edges(node_b, data=True)]
                out_edges_sorted = {e['output_index'] : e for e in out_edges}
                out_edges_sorted = sorted(out_edges_sorted, key=out_edges_sorted.get)
                # NEED ERROR CHECKING HERE
                # (psuedo) if n_out == n_expected_out
                for i,out_edge in out_edges_sorted:
                    out_edge['data'] = outputs[i]

                n_edges_loaded = 0

            n_edges_loaded + 1







    # def _get_topology(self):
        # # first node is always an Input for the first iteration
        # # first nodes will not have any dependents
        #
        # output_names = {}
        # input_data = {}
        # current_node = None
        #
        # # this for loop goes through EDGE BY EDGE
        # # and queues data for the next node in the dictionary "input_data"
        # # - Jeff
        # order = nx.topological_sort( nx.line_graph(self.graph) )
        # for node_a, node_b, edge_idx in order:
        #     print(node_a, "---",edge_idx,"--->", node_b)
        #     # FIRST ITERATION ONLY
        #     if current_node is None:
        #         current_node = node_b
        #
        #     # while our incoming edges are still from Inputs, we have to
        #     # queue the input data in the var data dict so we can begin tasks
        #     prior_task = self.graph.nodes[node_a]['task_processor']
        #     if isinstance(prior_task, Input):
        #         # grab the name of the variable and then queue data in the dict
        #         input_name = self.graph.edges[node_a, node_b, edge_idx]['var_name']
        #         self.vars[input_name]['data'] = prior_task._pipeline_process()
        #         # print("queuing {} data".format(prior_task))
        #
        #     # if the node_b hasn't changed, we are still iterating through edges
        #     # incoming into this node and thus we keep queuing data
        #     # for the first iteration, node_b will be defined, but  current_node
        #     # will be None
        #     if node_b == current_node:
        #         # retrieve the data from the self.vars dict and queue it for
        #         # next task
        #         # this method relies on the data dict being updated between
        #         # iterations of this generator (in the process function
        #         edge = self.graph.edges[node_a, node_b, edge_idx]
        #         input_data[ edge['index'] ] = self.vars[ edge['var_name'] ]['data']
        #         # print("queuing input for ", self.graph.nodes[node_b]['task_processor'] )
        #
        #     # otherwise, we are at a new connection and it is time to compute
        #     # using all the data we've queued
        #     else:
        #         # yield the blockdata required to compute the next step
        #         # (p.s. a task is a generic name for a block/sub-pipeline
        #         task = self.graph.nodes[current_node]['task_processor']
        #         # print("computing ", task)
        #
        #         # sort the inputs by their input index into the task
        #         inputs_list = tuple(input_data[k] for k in sorted(input_data.keys()))
        #
        #         # fetch the names of the outputs sorted by output index from the task
        #         out_edges_attrs = [e[2] for e in self.graph.out_edges(node_b, data=True)]
        #         output_names_dict = {edge_attrs['index'] : edge_attrs['var_name'] for edge_attrs in out_edges_attrs}
        #         output_names = sorted(output_names, key=output_names_dict.get)
        #
        #         yield task, inputs_list, output_names
        #
        #
        #     current_node = node_b
        #     # reset local data for next iteration of generator
        #     input_data = {}



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

        return {edge['var_name'] : edge['data'] for _,_,edge in self.graph.edges()}


    def clear(self):
        """resets all data temporarily stored in the graph"""
        for var in self.vars.values():
            var['data'] = None

    def draw(self):
        plt.cla()
        nx.draw_networkx(self.graph,
                            pos=nx.planar_layout(self.graph),
                            labels= { n : self.graph.node[n]['name'] for n in self.graph.nodes()} )  # use spring layout
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
    def __get_logger_name(basename, sibling_id, uuid):
        """generates a unique logger name that contains both a sibling id
        (a random string that will be persistent across all copies and unpickled
        versions of this object) and a uuid (which is unique to this exact
        object instance)
        (only the last six chars of each hash is used, so it's technically possible
        for this name to not be unique) - if you need a truly unique ID, then
        use obj.uuid
        """
        return "{basename} #{sibling_id}-{uuid}".format(basename=basename,
                                                sibling_id=sibling_id[-6:],
                                                uuid=uuid[-6:])



# import imagepypelines as ip
#
# # you can insert your own functions Really easily!!!
# @ip.blockify(io_map={'amplitude':ip.Array([None,1]) })
# def calculate_orientation(amplitude, phase_difference):
#     #
#     # * some code to calculate orientation *
#     #
#     return orientation
#
# graph = {   # create placeholder variables for input data
#             'measure_coil' : ip.Input(0),
#             'ref_coil' : ip.Input(1),
#             # move the data into a wavelet plane
#             'meas_wavelet' : (ip.Cwt(), 'measure_coil'),
#             'ref_wavelet' : (ip.Cwt(), 'ref_coil'),
#             # filter the data to 12Khz +/- 1Hz
#             'meas_filtered_12k' : (ip.GaussianFilter(mean=12e3, sigma=1), 'meas_wavelet'),
#             'ref_filtered_12k' : (ip.GaussianFilter(mean=12e3, sigma=1), 'ref_wavelet'),
#             # calculate amplitude and phase of each coil
#             'meas_amp' : (ip.Abs(), 'meas_filtered_12k'),
#             'meas_phase' : (ip.Angle(), 'meas_filtered_12k'),
#             'ref_amp' : (ip.Abs(), 'ref_filtered_12k'),
#             # calculate phase difference between the reference and measure_coil
#             'phase_diff' : (ip.Sub2(), 'meas_phase', 'ref_phase'),
#             'orientation' : ( calculate_orientation, 'meas_amp', 'phase_difference')
#             }
#
# coil_task = ip.Pipeline(graph)
# # Coil processor can now be saved, deployed to a server, or used to
# # partially document your algorithm for a paper!
#
# orientation = coil_processor.process(measurment_coil, reference_coil)













    # def process(self, *data, **named_data):
    #     # JM: TODO
    #     # check to make sure all data is a list or row separable array
    #
    #     # Save all data passed in to a dictionary with a unique identifier
    #     self.data = {'pipeline_input $%s' % i for i in range(len(data)) :
    #                     d for d in data}
    #
    #     # check to make sure the 'named_data' dictionary contains already
    #     # existing keys, this is done by checking key intersection using the
    #     # '&' operator
    #     if len( self.data.keys() & named_data.keys() ) > 0:
    #         raise KeyError("illegal input variable name key")
    #     self.data.update(named_data)
    #
    #     # JM: TODO
    #     # add logging to follow along with this
    #     for node in self.data.keys():
    #         self.graph.add_node
    #
    #

    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #     # iterate through processors and yield them
    #     # for node_a, node_b, edge_idx in uuid_order:
    #     #     processor_a = self.graph.nodes[node_a]['obj']
    #     #     processor_b = self.graph.nodes[node_b]['obj']
    #     #     yield processor_a, processor_b, edge_idx
    #
    #
    # def draw(self, display=True):
    #     """generates a matplotlib figure that graphically represents the
    #     graph for a human
    #
    #     Args:
    #         display(bool): whether or not to display the graph, or just return
    #             the Figure
    #
    #     Returns:
    #         matplotlib.pyplot.Figure: figure which represents the graph
    #     """
    #     # real code here:
    #     fig = plt.figure()
    #     axes = fig.add_subplot(111)
    #
    #     # get positioning for nodes
    #     pos = nx.spring_layout(self.graph)
    #
    #     nx.draw(self.graph,
    #                 pos,
    #                 with_labels=True,
    #                 font_weight='bold',
    #                 node_color='orange')
    #     if display:
    #         plt.show()
    #
    #     return fig
    #
    #
    # @property
    # def inputs(self):
