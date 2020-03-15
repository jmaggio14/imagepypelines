# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018-2020 Jeff Maggio, Nathan Dileas, Ryan Hartzell
from ..Logger import get_logger, error as iperror, info as ipinfo
from .Block import Block
from .Data import Data
from .block_subclasses import Input, Leaf, PipelineBlock
from .constants import UUID_ORDER
from .Exceptions import PipelineError
from .io_tools import passgen

from cryptography.fernet import Fernet
import inspect
import numpy as np
from uuid import uuid4
import networkx as nx
import pickle
import hashlib
import copy

ILLEGAL_VAR_NAMES = ['fetch','skip_checks']
"""illegal or reserved names for variables in the graph"""

class Pipeline(object):
    """processing algorithm manager for simple pipeline construction

    < RYAN I NEED YOU HERE >


    Attributes:
        uuid(str): hex uuid for this pipeline
        name(str): user specified name for this pipeline, used to generate
            the unique id. defaults to "Pipeline" or the name of your subclass
        logger(:obj:`ImagepypelinesLogger`): Logger object for this pipeline
        graph(:obj:`networkx.MultiDiGraph`): Multi-Edge directed task graph
            which stores all data and algorithmic order
        vars(dict): dict to track the block that generates the each variable,
            keys are variable names, values are a subdictionary containing
            'block_node_id' and 'block'
        indexed_inputs(:obj:`list` of :obj:'str'): sorted list of indexed input
            variable names. (the indexed arguments for the process function)
        keyword_inputs(:obj:`list` of :obj:'str'): alphabetically sorted list of
            unindexed input variable names (the keyword arguments for the
            process function)
        _inputs(dict): dictionary internally to access Input objects used to
            queue data into the pipeline


    Example:
        >>> import imagepypelines as ip
        >>>
        >>> @ip.blockify( kwargs=dict(value=10) )
        >>> def add_val(a,b,value):
        >>>     return a+value, b+value
        >>>
        >>> @ip.blockify( kwargs=dict(value=5) )
        >>> def minus_val(a,b,value):
        >>>     return a-value, b-value
        >>>
        >>> tasks = {
        >>>         # inputs
        >>>         'zero' : ip.Input(0),
        >>>         'one' : ip.Input(1),
        >>>         # operations
        >>>         ('ten','eleven') : (add_val, 'zero', 'one'),
        >>>         ('twenty','eleven2') : (add_val, 'ten', 'one'),
        >>>         ('fifteen', 'six') : (minus_val, 'twenty', 'eleven'),
        >>>         ('twentyfive','twentyone') : (add_val, 'fifteen','eleven2'),
        >>>         ('negativefour', 'negativefive') : (minus_val, 'one', 'zero'),
        >>>         }
        >>>
        >>> # pipeline1 - raw construction
        >>> pipeline1 = ip.Pipeline(tasks, 'Pipeline1')
        >>> # pipeline1.draw(show=True)
        >>>
        >>> processed1 = pipeline1.process([0,0], [1,1])
        >>> # print(processed1)
        >>>
        >>>
        >>> # pipeline2 - construction from task dict
        >>> static_constructor = pipeline1.get_tasks()
        >>>
        >>> pipeline2 = ip.Pipeline(static_constructor, name="Pipeline2")
        >>> processed2 = pipeline2.process([0,0], one=[1,1])


    """
    def __init__(self, tasks={}, name=None):
        """initializes the pipeline with a user-provided graph (tasks)

        Args:
            tasks (dict,:obj:`Pipeline`): dictionary of tasks to define this
                pipeline's graph or another pipeline to replicate.
            name (str): name used to generate the logger name
        """
        self.uuid = uuid4().hex # unique univeral hex ID for this pipeline
        if name is None:
            name = self.__class__.__name__
        self.name = name # string name - used to generate the id

        # build the logger for this pipeline
        self.logger = get_logger( self.id ) # logging object

        # GRAPHING
        self.graph = nx.MultiDiGraph() # networkx graph keeping track of tasks
        self.vars = {} # dict of var_names and the nodes that create them

        # PROCESS / internal tracking
        self.indexed_inputs = [] # sorted list of indexed input variable names
        self.keyword_inputs = [] # alphabetically sorted list of unindexed inputs
        self._inputs = {} # dict of input_name: Input_object

        # If a pipeline is passed in, then retrieve tasks and replicate our
        # pipeline
        if isinstance(tasks, Pipeline):
            tasks = tasks.get_tasks()



        self.update(tasks)


    ############################################################################
    #                       primary frontend functions
    ############################################################################
    def update(self, tasks={}):
        """updates the pipeline's graph with a dict of tasks

        `update` will modify and change many instance variables of the pipeline.
        Despite its generic name, it can only add tasks to the pipeline, not
        remove them. `update` is called internally to the pipeline during
        instantiation.

        Args:
            tasks(dict): dictionary of tasks to define this pipeline's graph

        """
        ########################################################################
        #                           HELPER FUNCTIONS
        ########################################################################
        def _add_to_vars(var):
            # make sure variable name is a string
            if not isinstance(var,str):
                msg = "graph vars must be a string, not %s" % type(var)
                self.logger.error(msg)
                raise TypeError(msg)

            # check if variable name already exists
            if var in self.vars.keys():
                msg = "\"%s\" cannot be defined more than once" % var
                self.logger.error(msg)
                raise ValueError(msg)

            # check if variable name is illegal
            if var in ILLEGAL_VAR_NAMES:
                msg = "var cannot be named one of %s" % ILLEGAL_VAR_NAMES
                self.logger.error(msg)
                raise PipelineError(msg)

            self.vars[var] = {'block_node_id':None, # will always be defined
                                'block':None # will always be defined
                                }

        def _add_input(inpt, outputs, node_uuid):
            # track what inputs are required so we can populate
            # them with arguments in self.process
            if len(outputs) != 1:
                msg = "Inputs must define exactly one output"
                self.logger.error(msg)
                raise PipelineError(msg)

            # add the input block to a tracking dictionary
            self._inputs[outputs[0]] = inpt

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
                        raise PipelineError("Input blocks cannot take any arguments")

                for output in outputs:
                    self.vars[output]['block_node_id'] = node_uuid
                    self.vars[output]['block'] = block

                # check this task's setup using the block.check_setup function
                block.check_setup(args)

                # add the task to the graph
                self.graph.add_node(node_uuid,
                                    block=block,
                                    args=args,
                                    outputs=outputs,
                                    **block.get_default_node_attrs(),
                                    )



            else: # something other than a block or of tuple (block, var1, var2,...)
                raise PipelineError("invalid task definition, must be block or tuple: (block, 'var1', 'var2',...)")

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
        for inpt_name, inpt in self._inputs.items():
            # check if the input index is defined
            if isinstance(inpt.index,int):
                self.indexed_inputs.append(inpt_name)
            else:
                self.keyword_inputs.append(inpt_name)

        # sort the positonal inputs by index
        self.indexed_inputs.sort(key=lambda x: self._inputs[x].index)
        # sort keyword only inputs alphabetically
        self.keyword_inputs.sort()


        # check to make sure an input index isn't defined twice
        indices_used = [self._inputs[x].index for x in self.indexed_inputs]
        if len(set(indices_used)) != len(indices_used):
            # Note: add more verbose error message
            msg = "Input indices cannot be reused"
            self.logger.error(msg)
            raise PipelineError(msg)

        # check to make sure input indexes are consecutive (don't skip)
        if len(indices_used) > 0:
            if max(indices_used) + 1 != len(indices_used):
                # Note: add more verbose error message
                msg = "Input indices must be consecutive"
                self.logger.error(msg)
                raise PipelineError(msg)

        # log the current pipeline status
        msg = "{} tasks set up; process arguments are ({})".format(len(tasks), ', '.join(self.args))
        self.logger.info(msg)

    ############################################################################
    def process(self, *pos_data, fetch=None, skip_checks=False, **kwdata):
        """processes input data through the pipeline

        process first resets this pipeline, before loading input data into the
        graph and processing it.

        Note:
            The argument list for the Pipeline can be found with `Pipeline.args`

            MUST ADD FETCHES DOCUMENTATIONS
        """
        # reset all leftover data in this graph
        self.clear()

        # setup fetches
        if fetch is None:
            fetch = self.vars.keys()

        # --------------------------------------------------------------
        # STORING INPUTS - inside the input nodes
        # --------------------------------------------------------------
        all_inputs = self.args
        # store positonal arguments fed in
        ## NOTE: need error checking here (number of inputs, etc)
        for i,data in enumerate(pos_data):
            inpt = self._inputs[ all_inputs[i] ]
            # check if the data has already been loaded
            if inpt.loaded:
                msg = "'%s' has already been loaded" % self.indexed_inputs[i]
                self.logger.error(msg)
                raise PipelineError(msg)
            inpt.load(data)

        # store keyword arguments fed in
        ## NOTE: need error checking here (number of inputs, etc)
        for key, val in kwdata.items():
            inpt = self._inputs[key]
            # check if the data has already been loaded
            if inpt.loaded:
                msg = "'%s' has already been loaded" % key
                self.logger.error(msg)
                raise PipelineError(msg)
            inpt.load(val)

        # check to make sure all inputs are loaded
        data_loaded = True
        for key,inpt in self._inputs.items():
            if not inpt.loaded:
                msg = "data for \"%s\" must be provided" % key
                self.logger.error(msg)
                data_loaded = False

        if not data_loaded:
            raise PipelineError("insufficient input data provided")

        # --------------------------------------------------------------
        # PROCESS
        # --------------------------------------------------------------
        self._compute()

        # populate the output dictionary
        fetch_dict = {}
        for _,_,edge in self.graph.edges(data=True):
            if edge['var_name'] in fetch:
                fetch_dict[ edge['var_name'] ] = edge['data'].pop()

        # clear the graph of data to reduce memory footprint
        self.clear()

        return fetch_dict

    ############################################################################
    def block(self, *fetches):
        """generates a block that runs this pipeline internally

        Args:
            *fetches: variables to fetch from the pipeline in the order they
                should be outputed as

        Returns:
            :obj:`Block`: Block which will run the pipeline internally and
                retrieve the data specified by fetches
        """
        return PipelineBlock(self, fetch=fetches)


    ############################################################################
    def clear(self):
        """resets all edges in the graph, clears the inputs"""
        for _,_,edge in self.graph.edges(data=True):
            edge['data'] = None

        for inpt in self._inputs.values():
            inpt.unload()

    ############################################################################
    def draw(self, show=True, ax=None):
        # visualize(self, show, ax)
        pass

    # saving/loading
    ############################################################################
    def save(self, filename, passwd=None, protocol=pickle.HIGHEST_PROTOCOL):
        """pickles and saves a copy of the  pipeline to the given filename.
        Pipeline can be optionally encrypted

        Args:
            filename(str): the filename to save the pickled pipeline to
            passwd(str): password to encrypt the pickled pipeline with if
                desired, defaults to None
            protocol(int): pickle protocol to pickle pipeline with, defaults to
                pickle.HIGHEST_PROTOCOL

        Returns:
            str: the sha256 checksum for the saved file
        """
        encoded, checksum = self.to_bytes(passwd, protocol)
        # write the file contents
        with open(filename, 'wb') as f:
            f.write(encoded)

        return checksum

    ############################################################################
    @classmethod
    def load(cls, filename, passwd=None, checksum=None, name=None):
        """loads the pipeline from the given file

        Args:
            filename(str): the filename to load the pickled pipeline from
            passwd(str): password to decrypt the pickled pipeline with, defaults
                to None
            checksum(str): the sha256 checksum to check the file against
            name(str): new name for the pipeline. If left as None, then
                defaults to the old name of the pipeline

        Returns:
            :obj:`Pipeline`: the loaded pipeline
        """
        # fetch the raw file contents
        with open(filename,'rb') as f:
            raw_bytes = f.read()

        return cls.from_bytes(raw_bytes, passwd, checksum, name)

    ############################################################################
    def to_bytes(self, passwd=None, protocol=pickle.HIGHEST_PROTOCOL):
        """pickles a copy of the pipeline, and returns the raw bytes. Can be
        optionally encrypted

        Args:
            passwd(str): password to encrypt the pickled pipeline with if
                desired, defaults to None
            protocol(int): pickle protocol to pickle pipeline with, defaults to
                pickle.HIGHEST_PROTOCOL

        Returns:
            (tuple): tuple containing:

                bytes: the pickled and optionally encrypted pipeline
                str: the sha256 checksum for the raw bytes
        """
        # pickle the pipeline
        raw_bytes = pickle.dumps(self.copy(), protocol=protocol)

        # encrypt the pipeline if passwd is provided
        if passwd:
            fernet = Fernet( passgen(passwd) )
            encoded = fernet.encrypt(raw_bytes)
        else:
            encoded = raw_bytes

        return encoded, hashlib.sha256(encoded).hexdigest()

    ############################################################################
    @staticmethod
    def from_bytes(raw_bytes, passwd=None, checksum=None, name=None):
        """loads the pipeline from the given file without change

        Args:
            raw_bytes(bytes): the encoded pipeline in bytes format
            passwd(str): password to decrypt the pickled pipeline with, defaults
                to None
            checksum(str): the sha256 checksum to check the bytes against
            name(str): new name for the pipeline. If left as None, then
                defaults to the old name of the pipeline

        Returns:
            :obj:`Pipeline`: the loaded pipeline
        """
        # check the file checksum if provided
        if checksum:
            fchecksum = hashlib.sha256(raw_bytes).hexdigest()
            if fchecksum != checksum:
                msg = "'%s'checksum doesn't match" % filename
                iperror(msg)
                PipelineError(msg)

        # decrypt the file contents if passwd is provided
        if passwd:
            fernet = Fernet( passgen(passwd) )
            decoded = fernet.decrypt(raw_bytes)
        else:
            decoded = raw_bytes

        # load the pipeline
        pipeline = pickle.loads(decoded)

        # rename it if desired
        if name is not None:
            pipeline.rename(name)

        ipinfo("loaded {}".format(pipeline.id))
        return pipeline

    ############################################################################
    def copy(self, name=None):
        """returns a copy of the Pipeline, but not a copy of the blocks"""
        if name is None:
            name = self.name
        return Pipeline(self, name=name)

    ############################################################################
    def deepcopy(self, name=None):
        """returns a copy of the Pipeline including copies of all its blocks"""
        if name is None:
            name = self.name
        # iterate through all pipeline tasks
        already_copied = {}
        new_tasks = {}
        # for ('out1', 'out2'), (block, 'in1', 'in2')
        for task_outs, task_ins in self.get_tasks().items():
            old_block = task_ins[0]
            args = task_ins[1:]

            # if block is already copied, fetch the copied block for the new tasks
            if old_block.uuid in already_copied:
                new_block = already_copied[old_block.uuid]
            # otherwise copy the block if we haven't already copied it
            else:
                new_block = old_block.deepcopy()
                already_copied[old_block.uuid] = new_block

            new_tasks[task_outs] = (new_block,) + args

        return Pipeline(new_tasks, name=name)


    ############################################################################
    #                               internal
    ############################################################################
    def _compute(self):
        """executes the graph tasks. Relies on Input data being preloaded"""
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


    ############################################################################
    #                               util
    ############################################################################
    def get_tasks(self):
        """generates a dictionary task represenation of the pipeline, which can
        be used to make other pipelines.
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

    ############################################################################
    def get_predecessors(self, var):
        """fetches the names of the variables which must be computed/loaded
        before the given variable can be computed.

        Args:
            var(str): name of variable to find predecessors for

        Returns:
            set: an unordered set of the variables that must be computed before
                the given variable can be calculated.
        """
        # NOTE: we could possibly speed this function up by using a depth
        # finding algorithm instead?
        # define a recursive function to get edges from all predecessor nodes
        preds = set()
        nodes_checked = set()
        def _get_priors(node):
            for node_a,node_b,var_name in self.graph.in_edges(node,'var_name'):
                preds.add(var_name)
                # recursively add edges from the source node
                if node_a not in nodes_checked:
                    _get_priors(node_a)

            nodes_checked.add(node)

        _get_priors(self.vars[var]['block_node_id'])

        return preds

    ############################################################################
    def get_successors(self, var):
        """fetches the names of the variables which depend on this variable
        before they can be computed

        Args:
            var(str): name of variable to find successors for

        Returns:
            set: an unordered set of the variables that can only be computed
                once the given variable has been
        """
        # NOTE: we could possibly speed this function up by using a depth
        # finding algorithm instead?
        # define a recursive function to get edges from all successor nodes
        succs = set()
        nodes_checked = set()
        def _get_latters(node):
            for node_a,node_b,var_name in self.graph.out_edges(node,'var_name'):
                succs.add(var_name)
                # recursively add edges from the source node
                if node_b not in nodes_checked:
                    _get_latters(node_b)

            nodes_checked.add(node)

        _get_latters(self.vars[var]['block_node_id'])

        # remove the name of the variable
        succs.remove(var)
        return succs

    ############################################################################
    def assign_input_index(self, var, index):
        """reassigns the index for this variable in the process argument list"""
        # reset the input index to a new one
        self._inputs[var].set_index(index)
        self.update()

    ############################################################################
    def debug_pickle(self, pickle_protocol=pickle.HIGHEST_PROTOCOL):
        """helper function to debug what part of a block is not serializable"""
        error = False

        # fetch the static graph represenation
        static = self.get_tasks()

        # iterate through all tasks and check if their components are serializable
        raise_error = False
        for task in static.values():
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

    ############################################################################
    def rename(self, name):
        """renames the Pipeline to the given name. The id is reset in this process"""
        if not isinstance(name,str):
            raise PipelineError("name must be string")

        self.logger.warning("being renamed from '%s' to '%s'" % (self.name, name))
        old_name = self.name
        self.name = name
        # reset the logger with the new id
        self.logger = get_logger(self.id)
        # log the new name
        self.logger.warning("renamed from '%s' to '%s'" % (old_name, self.name))
        return self


    ############################################################################
    #                               special
    ############################################################################
    # COPYING & PICKLING
    def __getstate__(self):
        return self.__dict__

    ############################################################################
    def __setstate__(self, state):
        """resets the uuid in the event of a copy"""
        state['uuid'] = uuid4().hex
        self.__dict__.update(state)

    ############################################################################

    ############################################################################
    #                               properties
    ############################################################################
    @property
    def id(self):
        """str: an unique id for this pipeline

        This id is a combination of the pipeline's non-unique name and
        part of it's uuid (last 6 characters by default).
        The entropy of this id can be increased by increasing ImagePypelines
        UUID_ORDER variable
        """
        return "{}#{}".format(self.name,self.uuid[-UUID_ORDER:])

    ############################################################################
    @property
    def execution_order(self):
        """:obj:`Generator`: topologically sorted edges of the pipeline"""
        return nx.topological_sort( nx.line_graph(self.graph) )

    ############################################################################
    @property
    def args(self):
        """:obj:`list` of :obj:`str`: arguments in the order they are expected"""
        return self.indexed_inputs + self.keyword_inputs

    ############################################################################
    @property
    def n_args(self):
        """int: number of arguments for the process function"""
        return len(self.args)

    ############################################################################
    @property
    def blocks(self):
        """:obj:`set` of :obj:`Block`: unordered set of pipeline blocks"""
        blocks = set()
        for _,block in self.graph.nodes(data='block'):
            # ignore leaves
            if not isinstance(block, Leaf):
                blocks.add(block)
        return blocks





# END
