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
    """Block that will run anmy fucntin you give it, either unfettered through
    the __call__ function, or with optional hardcoded parameters for use in a
    pipeline. Typically the FuncBlock is only used in the `blockify` decorator
    method.

    Args:
        func (function): the function you desire to turn into a block
        preset_kwargs (dict): preset keyword arguments, typically used for
            arguments that are not data to process
    """
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
        required = spec.args[:num_required]

        exec_string = \
        """
        def process(self,{required}):
            return self.func({required},**self.preset_kwargs)
        """.format(required = ', '.join(required))
        exec_locals = {}
        exec(exec_string, {}, exec_locals)
        self.process = exec_locals['process']
        super().__init__()

    def __call__(self,*args,**kwargs):
        """returns the exact output of the user defined function without any
        interference or interaction with the class
        """
        return self.func(*args,**kwargs)


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



class Input(BatchBlock):
    def __init__(self,index=None):
        self.index = index
        self.data = None
        super().__init__()

    def load(self, data):
        self.data = data

    def batch_process(self):
        return self.data

    def unload(self,):
        self.data = None




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

        self._build_graph(user_graph=graph)

        self.vars = {}
        self.positional_inputs = []


    def _build_graph(self,user_graph):

        # add all variables defined in the graph to a dictionary
        # quick helper function to add a node to the graph
        def _add_to_vars(var):
            if not isinstance(var,str):
                raise TypeError("graph vars must be a string")

            self.vars[var] = {'dependents':set(),
                                'processor':None # will always be defined
                                }


        #### FIRST FOR LOOP - defining the variables that we'll be using
        for var in user_graph.keys():
            # for str defined dict keys like 'x' : (func, 'a', 'b')
            if isinstance(var, str):
                _add_to_vars(var)

            # for tuple defined dict keys like ('x','y') : (func, 'a', 'b')
            elif isinstance(var,(tuple,list)):
                for n in var:
                    _add_to_vars(var)

        #### SECOND FOR LOOP - adding all nodes to the graph
        # reiterate through the graph definition to define inputs and outputs
        for outputs,definition in user_graph.items():
            # if multiple block outputs are defined, then we need a for loop
            if not isinstance(outputs,(tuple,list)):
                outputs = [outputs]

            # GETTING GRAPH INPUTS
            # e.g. - 'x': ip.Input(),
            if isinstance(definition, Input):
                # add this variables processor to it's attrs
                # these vars will not have any dependents
                for output in outputs:
                    self.vars[output]['processor'] = definition.uuid

                # add the processor to the graph
                self.graph.add_node(definition.uuid,
                                    definition.get_default_node_attrs(),
                                    processor=None,
                                    dependents=None)

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

                # update the dependents for all of these outputs
                for output in outputs:
                    self.vars[output]['dependents'].update(inpts)


        # THIRD FOR LOOP - drawing edges
        for var_name,attrs in self.vars.items():
            node_b = attrs['processor'].uuid
            current_node = self.graph.nodes[node_b]

            # connect all dependents to the variable node
            for node_a in attrs['dependents']:
                input_index = current_node['inputs'].index(var)
                input_name = current_node['processor'].inputs[input_index]

                self.graph.add_edge(node_a,
                                    node_b,
                                    var_name=var_name,
                                    index=input_index,
                                    name=input_name)


    def _get_topology(self):
        # first node is always an Input for the first iteration
        # first nodes will not have any dependents
        order = nx.topological_sort(nx.line_graph(self.graph))

        dependent_data = {}
        output_names = {}
        current_node = None
        for node_a, node_b, edge_idx in order:
            # we've reached the end of the edges for this connection
            if node_b != current_node:
                processor = self.graph.nodes[current_node]['processor']
                inputs = [dependent_data[k] for k in sorted(dependent_data.keys())]
                output_names = [output_names[k] for k sorted(output_names.keys())]
                yield processor, inputs, output_names

                dependent_data = {}
                output_names = {}
                current_node = node_b

            else:
                # retrieve the data from the data dict and add it to dependent_data
                # this method relies on the data dict being updated between
                # iterations of this generator
                edge = self.graph.edges[node_a, node_b, edge_idx]
                dependent_data[ edge['index'] ] = self.data_dict[edge['index']])
                output_names[ edge['index'] ] = edge['var_name']


    def process(self,**named_data):
        self.data_dict = named_data

        for processor, input_data, output_names in self._get_topology():
            # processor is a block
            if isinstance(processor,BaseBlock):
                outputs = processor._pipeline_process(*input_data)
            # processor is a pipeline
            else:
                outputs = processor.process(*input_data)

            # add data to the data_dict
            for name,output in zip(output_names, outputs):
                self.data_dict[name] = output


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
# coil_processor = ip.Pipeline(graph)
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
