# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018 - 2020 Jeff Maggio, Jai Mehra, Ryan Hartzell
from ..Logger import get_logger, MASTER_LOGGER
from .Block import Block
from .Data import Data
from .block_subclasses import Input, Leaf, PipelineBlock
from .constants import UUID_ORDER
from .Exceptions import PipelineError
from .io_tools import passgen
from .util import Timer
from .DashboardComm import DashboardComm

from cryptography.fernet import Fernet
import inspect
import numpy as np
from uuid import uuid4
import networkx as nx
from networkx.readwrite import json_graph
import hashlib
import copy
import itertools
import dill
import json

STATUS_NOT_STARTED = "not started"
"""status constant for nodes that haven't yet been started"""

STATUS_PROCESSING  = "processing"
"""status constant for nodes that are currently processing"""

STATUS_COMPLETE    = "done"
"""status constant for nodes that have completed their work"""

MSG_GRAPH  = "graph"
"""message type for graph messages"""

MSG_STATUS = "status"
"""message type for status messages"""

MSG_RESET  = "reset"
"""message type for reset messages"""

MSG_ERROR  = "block_error"
"""message type for error messages"""

MSG_DELETE  = "delete"
"""message type for delete messages"""

PIPELINE_SOURCE_TYPE = "pipeline"

ILLEGAL_VAR_NAMES = ['fetch','skip_enforcement']
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
        _inputs(dict): dictionary internally used to access Input objects for
            queuing data into the pipeline

    Pipeline Graph Information:
        Nodes are dictionaries representing tasks. They contain:
            'block'   : block object for this task,
            'args'    : names of the task inputs for this block,
            'outputs' : names of the task outputs produced by this block,
            'name'    : string name of the node for visualization purposes,
            'color'   : color of the node for visualization purposes,
            'shape'   : shape of the node for visualization purposes,
            'class_name' : name of the class, frequently identical to the name
            'validation_time': time required to validate incoming data if applicable
            'processing_time' : time required to process the data using this node
            'avg_time_per_datum': average processing time for each datum
            'num_in' : number of datums coming into this node
            'n_batches' : number of batches for this node
            'pid' : process id for this node
            'status': processing status. one of: ('not started', 'processing', 'done')
            <plus other attributes defined by the user in Block.get_default_node_attrs()>

        Pipeline edges are dictionaries containing the following:
            'var_name'        : name of the variable in task definition
            'out_index'       : output index from the source node,
            'in_index'        : input index for the target node,
            'name'            : name target block's argument at the in_index
            'same_type_for_all_datums'    : whether or not this data is a homogenus container
            'data_stored_in'  : the type of the container used to house the data (list, ndarray, etc)
            'n_datums'        : number of items of data in this edge
            'datum_type'      : the type of data contained, this is only
                                guarenteed to be accurate is same_type_for_all_datums is True
            'node_a'          : source node uuid
            'node_b'          : target node uuid
            'data'            : data for this edge




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
    def __init__(self, tasks=None, name=None):
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
        self.logger = get_logger(self.id, pipeline=self) # logging object

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
        elif isinstance(tasks, dict):
            tasks = tasks
        elif tasks is None:
            tasks = {}
        else:
            raise TypeError("'tasks' not a valid Pipeline, task graph dictionary, nor 'None'.")

        # build the dashboard comm object
        self.dashcomm = DashboardComm()

        # update the tasks
        self.update(tasks)


    ############################################################################
    #                       primary frontend functions
    ############################################################################
    def update(self, tasks=None, predict_compatibility=True):
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
                msg = f"graph vars must be a string, not {type(var)}"
                self.logger.error(msg)
                raise TypeError(msg)

            # check if variable name already exists
            if var in self.vars.keys():
                msg = f"variable \"{var}\" cannot be defined more than once"
                self.logger.error(msg)
                raise ValueError(msg)

            # check if variable name is illegal
            if var in ILLEGAL_VAR_NAMES:
                msg = f"{var} cannot be named one of {ILLEGAL_VAR_NAMES}"
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

        if tasks is None:
            tasks = {}

        ########################################################################
        #           Define the variables we'll be using for these tasks
        ########################################################################
        # add all variables defined in the graph to a dictionary
        for var in tasks.keys():
            print(var)
            # for tuple defined dict keys like ('x','y') : (block, 'a', 'b')
            if isinstance(var,(tuple,list)):
                for v in var:
                    _add_to_vars(v)

            # for str defined dict keys like 'x' : (block, 'a', 'b')
            else:
                _add_to_vars(var)



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
                                    validation_time=None,
                                    processing_time=None,
                                    avg_time_per_datum=None,
                                    num_in=None,
                                    n_batches=None,
                                    pid=None,
                                    status=STATUS_NOT_STARTED,
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
                                        same_type_for_all_datums="unknown",
                                        n_datums=0,
                                        datum_type=None,
                                        data_stored_in="unknown",
                                        node_a = node_a,
                                        node_b = node_b,
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
        for node_id,attrs in self.graph.nodes(data=True):
            # if the node already has outputs, we don't need a leaf out of it
            if self.graph.out_degree(node_id) == len(attrs['outputs']):
                continue
            # if the end node is a Leaf already, then we don't need another leaf
            elif isinstance(attrs['block'],Leaf):
                    continue
            else:
                bad_edges = []
                drawn_edges = tuple(self.graph.out_edges(node_id, data='var_name'))
                for var_name in attrs['outputs']:
                    if var_name not in drawn_edges:
                        bad_edges.append(var_name)

                end_nodes.append( (node_id,attrs,bad_edges) )

        for node_id,node_attrs,bad_edges in end_nodes:
            # this is a final node of the pipeline, so we need to draw a
            # leaf for each of its output edges
            for i,end_name in enumerate(bad_edges):
                # add the leaf
                leaf = Leaf(end_name)
                leaf_uuid = leaf.name + uuid4().hex + '-node'
                self.graph.add_node(leaf_uuid,
                                    block=leaf,
                                    args=(end_name,),
                                    outputs=(end_name,),
                                    validation_time=None,
                                    processing_time=None,
                                    avg_time_per_datum=None,
                                    num_in=None,
                                    n_batches=None,
                                    pid=None,
                                    status=STATUS_NOT_STARTED,
                                    **leaf.get_default_node_attrs()
                                    )

                # edge key is {var_name}:{out_index}-->{in_index}
                edge_key = "{}:{}-->{}".format(end_name, i, 0)
                # draw the edge to the leaf
                # no need to check if it exists, because we just created the Leaf
                self.graph.add_edge(node_id,
                                    leaf_uuid,
                                    key=edge_key,
                                    var_name=end_name, # name assigned in graph definition
                                    out_index=i,
                                    in_index=0,
                                    name=end_name, # name of node_b's process argument at the index
                                    same_type_for_all_datums="unknown",
                                    n_datums=0,
                                    datum_type=None,
                                    data_stored_in="unknown",
                                    node_a = node_id,
                                    node_b = leaf_uuid,
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
        msg = "{} tasks set up; process arguments are ({},)".format(len(tasks), ', '.join(self.args))
        self.logger.info(msg)

        ########################################################################
        #                       Running Checks
        ########################################################################

        if predict_compatibility:
            # check to make sure there are compatible types
            for var in self.vars.keys():
                # check if there are compatible types
                if self.get_types_for(var) == tuple():
                    msg = "PREDICTED INCOMPATIBILITY : no compatible types for '%s'" % var
                    self.logger.warning(msg)
                # check if there are compatible shapes
                if self.get_shapes_for(var) == tuple():
                    msg = "PREDICTED INCOMPATIBILITY : no compatible shapes for '%s'" % var
                    self.logger.warning(msg)


        # iterate through edges and check if any blocks are expecting void data
        for node_a_id, node_b_id, var_name  in self.graph.edges(data="var_name"):
            block_a = self.graph.nodes[node_a_id]['block']
            block_b = self.graph.nodes[node_b_id]['block']

            # if block a is void, then we make sure block_b isn't a block
            # expecting data that won't exist (make sure block b isn't a leaf)
            if block_a.void:
                if not isinstance(block_b, Leaf):
                    msg = "INCOMPATIBILE EDGE: {block_b} is expecting '{var_name}' from {block_a}, but {block_a} is void (doesn't return data)"
                    msg.format(block_a=block_a,
                                block_b=block_b,
                                var_name=var_name)
                    self.logger.warning(msg)

        # print warning for vars that won't be computed
        noncomputable = self.noncomputable
        if len(noncomputable) > 0:
            msg = f"{noncomputable} won't be computed because they rely on data from void blocks (blocks that don't return data)"
            self.logger.warning(msg)

        # send along the new graph in a message to the Dashboards
        self.__send_graph_msg_to_dash()


    ############################################################################
    def process(self, *pos_data, fetch=None, skip_enforcement=False, **kwdata):
        """processes input data through the pipeline

        process first resets this pipeline, before loading input data into the
        graph and processing it.

        Note:
            The argument list for the Pipeline can be found with `Pipeline.args`

        Warning:
            MUST ADD FETCHES DOCUMENTATIONS
        """
        # setup fetches
        if fetch is None:
            fetch = self.vars.keys()

        # clear any data already in the graph, and send a message to the dashboard(s)
        self.reset()

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
        self.__compute(skip_enforcement)

        # populate the output dictionary
        fetch_dict = {}
        for _,_,edge in self.graph.edges(data=True):
            print(edge['var_name'])
            if edge['var_name'] in fetch:
                if edge['data'] is None:
                    fetch_dict[ edge['var_name'] ] = None #Could eventually be ip.Void or ip.NULL type
                else:
                    fetch_dict[ edge['var_name'] ] = edge['data'].grab()

        # clear the graph of data to reduce memory footprint
        self.clear()

        return fetch_dict

    ############################################################################
    def process_and_grab(self, *pos_data, fetch, skip_enforcement=False, **kwdata):
        """processes input data through the pipeline, but returns a tuple with
        the specified fetches

        process first resets this pipeline, before loading input data into the
        graph and processing it.

        Note:
            The argument list for the Pipeline can be found with `Pipeline.args`

        Warning:
            MUST ADD FETCHES DOCUMENTATIONS
        """

        fetch_dict = self.process(*pos_data,
                                    fetch=fetch,
                                    skip_enforcement=skip_enforcement,
                                    **kwdata)
        return tuple( fetch_dict[k] for k in fetch )

    ############################################################################
    def asblock(self, *fetches):
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
        """clears all edges in the graph and unloads the input nodes. Does not
        update the remote dashboard"""
        # unload all edge data
        for _,_,edge in self.graph.edges(data=True):
            edge['data'] = None

        # unload all input data
        for inpt in self._inputs.values():
            inpt.unload()

    ############################################################################
    def reset(self):
        """resets all edges in the graph, resets the inputs (and updates the dashboards)"""
        self.clear()
        # send a message to the dashboards saying the pipeline has been reset
        self.__send_reset_msg_to_dash()

    ############################################################################
    def draw(self, show=True, ax=None):
        # visualize(self, show, ax)
        pass

    # saving/loading
    ############################################################################
    def save(self, filename, passwd=None):
        """serializes and saves a copy of the pipeline to the given filename.
        Pipeline can be optionally encrypted

        Args:
            filename(str): the filename to save the serialized pipeline to
            passwd(str): password to encrypt the serialized pipeline with if
                desired, defaults to None

        Returns:
            str: the sha256 checksum for the saved file
        """
        encoded, checksum = self.to_bytes(passwd)
        # write the file contents
        with open(filename, 'wb') as f:
            f.write(encoded)

        return checksum

    ############################################################################
    @classmethod
    def load(cls, filename, passwd=None, checksum=None, name=None):
        """loads the pipeline from the given file

        Args:
            filename(str): the filename to load the serialized pipeline from
            passwd(str): password to decrypt the serialized pipeline with, defaults
                to None
            checksum(str): the sha256 checksum to check the file against
            name(str): new name for the pipeline. If left as None, then
                defaults to the old name of the pipeline

        Returns:
            :obj:`Pipeline`: the loaded pipeline

        Warning:
            Serilized data can be a security risk! For sensitive applications,
            use the `checksum` parameter. ImagePypelines can use this to ensure
            the data hasn't been tampered with.

            for more information about serialization security, see:
            https://docs.python.org/3.8/library/pickle.html
        """
        # fetch the raw file contents
        with open(filename,'rb') as f:
            raw_bytes = f.read()

        return cls.from_bytes(raw_bytes, passwd, checksum, name)

    ############################################################################
    def to_bytes(self, passwd=None):
        """serialized a copy of the pipeline, and returns the raw bytes. Can be
        optionally encrypted

        Args:
            passwd(str): password to encrypt the serialized pipeline with if
                desired, defaults to None
        Returns:
            (tuple): tuple containing:

                bytes: the serialized and optionally encrypted pipeline
                str: the sha256 checksum for the raw bytes
        """
        raw_bytes = dill.dumps(self.copy())

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
        """loads the pipeline from the given bytes

        Args:
            raw_bytes(bytes): the encoded pipeline in bytes format
            passwd(str): password to decrypt the serialized pipeline with, defaults
                to None
            checksum(str): the sha256 checksum to check the bytes against
            name(str): new name for the pipeline. If left as None, then
                defaults to the old name of the pipeline

        Returns:
            :obj:`Pipeline`: the loaded pipeline

        Warning:
            Serialized data can be a security risk! For sensitive applications,
            use the `checksum` parameter. ImagePypelines can use this to ensure
            the data hasn't been tampered with.

            for more information about serialization security, see:
            https://docs.python.org/3.8/library/pickle.html
        """
        # check the file checksum if provided
        if checksum:
            fchecksum = hashlib.sha256(raw_bytes).hexdigest()
            if fchecksum != checksum:
                msg = "Invalid Checksum!"
                MASTER_LOGGER.error(msg)
                PipelineError(msg)

        # decrypt the file contents if passwd is provided
        if passwd:
            fernet = Fernet( passgen(passwd) )
            decoded = fernet.decrypt(raw_bytes)
        else:
            decoded = raw_bytes

        # load the pipeline
        pipeline = dill.loads(decoded)

        # rename it if desired
        if name is not None:
            pipeline.rename(name)

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
    def __format_edge_data_for_dash_msg(self, edge_data):
        """formats data for an edge to a sendable form,

        Relies on a copy of the edge being passed in so permanent changes to
        the graph aren't made
        """
        # delete the data from edge - we don't need it
        del edge_data['data']
        # convert classes to their strings names
        edge_data['datum_type'] = edge_data['datum_type'].__class__.__name__
        edge_data['data_stored_in'] = edge_data['data_stored_in'].__class__.__name__
        return edge_data

    def __send_graph_msg_to_dash(self):
        """sends a full description of the graph to the dashboard

        This includes the graph structure and documentation for all blocks
        """
        payload = {}
        payload['args'] = self.args

        # commented out as redundant on 07/12/20 - JM
        # # variables and the node id that creates them
        # vars = {key : val['block_node_id'] for key,val in self.vars.items()}
        # payload["vars"] = vars

        # create a dictionary containing block summaries
        payload['block_docs'] = {}
        for block in self.blocks:
            payload['block_docs'][block.id] = block._summary()

        # copy the graph so we can modify it safely
        graph_copy = self.graph.copy()

        # populate the nodes metadata
        payload['nodes'] = {}
        for node_id,node_info in graph_copy.nodes(data=True):
            # delete the block from this copy - we don't need it
            del node_info['block']
            payload['nodes'][node_id] = node_info

        # populate the edge metadata
        payload['edges'] = {}
        for node_a,node_b,key,e_data in graph_copy.edges(keys=True, data=True):
            e_data = self.__format_edge_data_for_dash_msg(e_data)
            payload['edges']['|'.join((node_a,node_b,key))] = e_data


        # jsonify the graph in node-link format. see:
        # https://networkx.github.io/documentation/stable/reference/readwrite/json_graph.html
        payload['node-link'] = json_graph.node_link_data(graph_copy)
        msg = {'type' : MSG_GRAPH,
                'name' : self.name,
                'id' : self.id,
                'uuid' : self.uuid,
                'source_type' : PIPELINE_SOURCE_TYPE,
                'payload' : payload,
                }
        self.dashcomm.write_graph(self.id, json.dumps(msg))

    ############################################################################
    def __read_msg_from_dash(self):
        """Receives any messages sent from the dashboards"""
        msg = self.dashcomm.read()
        if msg:
            print(msg)

    ############################################################################
    def __send_status_msg_to_dash(self, node_id):
        """builds and sends a status message to the dashboards"""
        payload = {}
        # fetch pertinent metadata from the node
        node_info = self.graph.nodes[node_id].copy()
        del node_info['block'] # delete the block from this copy
        payload['nodes'] = {node_id : node_info}

        # fetch metadata for the incoming edges
        payload['edges'] = {}
        for node_a,node_b,key,e_data in self.graph.in_edges(node_id, keys=True, data=True):
            # delete the data object from this copy
            formatted_edge_data = self.__format_edge_data_for_dash_msg(e_data.copy())

            # update the edges dict
            payload['edges']['|'.join((node_a,node_b,key))] = formatted_edge_data

        # encode the message as json and send it
        msg = {'type' : MSG_STATUS,
                'name' : self.name,
                'id' : self.id,
                'uuid' : self.uuid,
                'source_type' : PIPELINE_SOURCE_TYPE,
                'payload' : payload,
                }
        self.dashcomm.write_status( json.dumps(msg) )

    ############################################################################
    def __send_reset_msg_to_dash(self):
        """builds and sends a reset message to the dashboards"""
        msg = {'type' : MSG_RESET,
                'name' : self.name,
                'id' : self.id,
                'uuid' : self.uuid,
                'source_type' : PIPELINE_SOURCE_TYPE,
                'payload' : {},
                }
        self.dashcomm.write_reset( json.dumps(msg) )

    ############################################################################
    def __send_block_error_msg_to_dash(self, node_id, error):
        """builds and sends an error message to the dashboards"""
        block = self.graph.nodes[node_id]['block']

        msg = {'type' : MSG_ERROR,
                'name' : self.name,
                'id' : self.id,
                'uuid' : self.uuid,
                'source_type' : PIPELINE_SOURCE_TYPE,
                'payload' : {
                            'node_id' : node_id,
                            'block_name' : block.name,
                            'block_id'   : block.id,
                            'block_uuid' : block.uuid,
                            'error_type' : error.__class__.__name__,
                            'error_msg'  : str(error),
                            },
                }
        self.dashcomm.write_error( json.dumps(msg) )

    ############################################################################
    def __send_delete_msg_to_dash(self):
        """builds and sends a delete message to the dashboards"""
        msg = {'type' : MSG_DELETE,
                'name' : self.name,
                'id' : self.id,
                'uuid' : self.uuid,
                'source_type' : PIPELINE_SOURCE_TYPE,
                'payload' : {},
                }
        self.dashcomm.write_delete( json.dumps(msg) )

    ############################################################################
    def __compute_block(self, node_id, skip_enforcement=False):
        """

        WARNING:
            this function should only be called if all incoming edges are
            populated with data. Ideally it should not be used outside the
            __compute function
        """
        try:
            self.graph.nodes[node_id]['status'] = STATUS_PROCESSING

            # UPDATE THE DASHBOARD
            # -----------------------------------
            self.__read_msg_from_dash()
            self.__send_status_msg_to_dash(node_id)

            # fetch the block for this node
            block = self.graph.nodes[node_id]['block']

            # ORGANIZE INPUT DATA FOR COMPUTATION
            # -----------------------------------
            # fetch input data for this node
            in_edges = [e[2] for e in self.graph.in_edges(node_id, data=True)]
            arg_data_dict = {e['in_index'] : e['data'] for e in in_edges}
            args = [arg_data_dict[k] for k in sorted( arg_data_dict.keys() )]

            # assign the task outputs to their appropriate edge
            analytics = {}

            # COMPUTE DATA IN THE BLOCK
            # -----------------------------------
            # (args will be empty for root blocks)
            outputs = block._pipeline_process(*args,
                                                    logger=self.logger,
                                                    force_skip=skip_enforcement,
                                                    analytics=analytics)

            # POPULATE OUTPUT EDGES FOR THIS NODE
            # -----------------------------------
            # update the graph with analytics for this block
            self.graph.nodes[node_id].update(analytics)

            # populate upstream edges with the data we need
            # get the output edges
            out_edges = [e[2] for e in self.graph.out_edges(node_id, data=True)]
            # NEED ERROR CHECKING HERE
            # (psuedo) if n_out == n_expected_out
            if block.void:
                # there's no output for this block, so we write None to the edges
                for out_edge in out_edges:
                    out_edge['data'] = None
            else:
                for out_edge in out_edges:
                    data = Data( outputs[out_edge['out_index']] )
                    out_edge['data'] = data
                    out_edge['same_type_for_all_datums'] = data.is_homogenus_container()
                    out_edge['data_stored_in'] = data.container_type
                    out_edge['n_datums'] = data.n_datums
                    out_edge['datum_type'] = data.datum_type

            # update node status
            self.graph.nodes[node_id]['status'] = STATUS_COMPLETE


            # update the dashboard
            self.__send_status_msg_to_dash(node_id)

        except Exception as error:
            self.__send_block_error_msg_to_dash(node_id, error)
            raise

    ############################################################################
    def __compute(self, skip_enforcement=False):
        """executes the graph tasks. Relies on Input data being preloaded"""
        ## NOTE:
        # add warning that for edges that are non-computable
        ###
        for node_a, node_b, edge_idx in self.execution_order:
            # check if node_a is a root node (no incoming edges)
            # these nodes can be computed and the edge populated
            # immmediately because they have no predecessors
            # NOTE: this will currently break if a root has more than one
            # output - JM
            # ROOT BLOCKS
            if self.graph.in_degree(node_a) == 0:
                self.__compute_block(node_a, skip_enforcement)


            # NON-ROOT BLOCKS
            # compute this node if all the data is queued
            in_edges = self.graph.in_edges(node_b, data=True)
            data_is_queued = all((e[2]['data'] is not None) for e in in_edges)
            if all((e[2]['data'] is not None) for e in in_edges):
                self.__compute_block(node_b, skip_enforcement)

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

        # start with every node node after this one - (so we don't include companion outputs)
        for _,next_node in self.graph.out_edges(self.vars[var]['block_node_id']):
            _get_latters(next_node)

        return succs

    ############################################################################
    def get_types_for(self, var):
        """fetches the enforced types for this variable of the pipeline.

        More specifically, these are the types that won't throw an error
        within the block

        Args:
            var(str): the name of the variable

        Returns:
            (:obj:`tuple` of :obj:`type`): the types enforced for
        the given variable
        """
        # INTERNAL HELPER FUNCTION
        def _dominant_type(types1, types2):
            """determines which set of types are dominant between two tuples of
            types
            """
            # make types a tuple if they aren't already to simply the code
            if (types1 is not None) and not isinstance(types1,(list,tuple,set)):
                types1 = (types1,)
            if (types2 is not None) and not isinstance(types2,(list,tuple,set)):
                types2 = (types2,)

            # if either type is None, then the other automatically supercedes
            if types1 is None:
                return types2
            elif types2 is None:
                return types1
            # both must lists/tuples of types - we want the intersection
            else:
                okay_types = set(types1).intersection( set(types2) )
                return tuple( okay_types )
        # END INTERNAL HELPER FUNC

        # Iterate through pipeline args and compute the dominant type
        dom_types = None
        # fetch the node that produced the variable
        source_node = self.vars[var]['block_node_id']
        # iterate through all nodes it's connected to and fetch their types
        for _,node_b,edge in self.graph.out_edges(source_node, data=True):
            # only if this out edge is for the given var
            if (edge['var_name'] == var):
                # fetch target block object
                target = self.graph.nodes[node_b]['block']
                # fetch the actual name of the argument in the target's process function
                target_arg = target.args[ edge['in_index'] ]
                # skip updating this target if its enforcement is disabled
                if target.skip_enforcement:
                    continue

                # compute and update the dominant type
                dom_types = _dominant_type(
                                            target.types.get(target_arg, None),
                                            dom_types
                                            )

        return dom_types

    ############################################################################
    def get_shapes_for(self, var):
        """fetches the enforced shapes for the given variable

        More specifically, these are the shapes that won't throw an
        error within the block

        Args:
            var(str): the name of the variable

        Returns:
            (:obj:`tuple` of :obj:`tuple`): the shapes enforced for
        the given variable
        """
        # INTERNAL HELPER FUNCTION
        def _dominant_shape(shape1, shape2):
            """determines which shape is dominant between shapes, or calculates
            the new compatible shape if it's required."""
            # if either shape is None, then the other automatically supercedes
            if shape1 is None:
                return shape2
            elif shape2 is None:
                return shape1
            # both must lists or tuples
            else:
                # if the ndim aren't the same, then there is no compatible shape
                if len(shape1) != len(shape2):
                    return tuple()

                new_shape = []
                # other we have to iterate through and find the dominant axes
                for ax1,ax2 in zip(shape1,shape2):
                    # if one axis is None, then the other is dominant
                    if ax1 is None:
                        new_shape.append(ax2)
                    elif ax2 is None:
                        new_shape.append(ax1)
                    # both must be integers
                    else:
                        if ax1 == ax2:
                            # if both axial lengths are identical, then we
                            # can append either to the new shape
                            new_shape.append(ax1)
                        else:
                            # if the axial lengths aren't identical, there is
                            # no compatible axis and thus no compatible shape
                            # so we return an empty shape
                            return tuple()

                return new_shape
        # END INTERNAL HELPER FUNC

        dom_shapes = (None,)
        # fetch the node that produced the variable
        source_node = self.vars[var]['block_node_id']
        # iterate through all nodes it's connected to and fetch their types
        for _,node_b,edge in self.graph.out_edges(source_node, data=True):
            # only if this out edge is for the given var
            if (edge['var_name'] == var):
                # fetch target block object
                target = self.graph.nodes[node_b]['block']
                # fetch the actual name of the argument in the target's process function
                target_arg = target.args[ edge['in_index'] ]
                # skip updating this target if its enforcement is disabled
                if target.skip_enforcement:
                    continue
                # fetch target shapes
                target_shapes = target.shapes.get(target_arg, None)
                # make target shapes an 1 elem iterable if it's None
                target_shapes = (None,) if target_shapes is None else target_shapes
                # calculate all possible shape permutations
                all_possible = itertools.product(
                                                set(target_shapes),
                                                set(dom_shapes)
                                                )

                # check every possible combination
                all_workable = []
                for shape1,shape2 in all_possible:
                    all_workable.append( _dominant_shape(shape1, shape2) )

                # remove empty tuples (i.e. incompatible shapes)
                dom_shapes = tuple(s for s in all_workable if s != tuple())
                #update the dominant type

            return dom_shapes

    ############################################################################
    def get_containers_for(self, var):
        """fetches the enforced containers for this variable of the pipeline.

        More specifically, these are the containers that won't throw an error
        within the block

        Args:
            var(str): the name of the variable

        Returns:
            (:obj:`tuple` of :obj:`type`): the containers enforced for
        the given variable
        """
        # INTERNAL HELPER FUNCTION
        def _dominant_container(containers1, containers2):
            """determines which set of containers are dominant between two tuples of
            containers
            """
            # make containers a tuple if they aren't already to simply the code
            if (containers1 is not None) and not isinstance(containers1,(list,tuple,set)):
                containers1 = (containers1,)
            if (containers2 is not None) and not isinstance(containers2,(list,tuple,set)):
                containers2 = (containers2,)

            # if either container is None, then the other automatically supercedes
            if containers1 is None:
                return containers2
            elif containers2 is None:
                return containers1
            # both must lists/tuples of containers - we want the intersection
            else:
                okay_containers = set(containers1).intersection( set(containers2) )
                return tuple( okay_containers )
        # END INTERNAL HELPER FUNC

        # Iterate through pipeline args and compute the dominant container
        dom_containers = None
        # fetch the node that produced the variable
        source_node = self.vars[var]['block_node_id']
        # iterate through all nodes it's connected to and fetch their containers
        for _,node_b,edge in self.graph.out_edges(source_node, data=True):
            # only if this out edge is for the given var
            if (edge['var_name'] == var):
                # fetch target block object
                target = self.graph.nodes[node_b]['block']
                # fetch the actual name of the argument in the target's process function
                target_arg = target.args[ edge['in_index'] ]
                # skip updating this target if its enforcement is disabled
                if target.skip_enforcement:
                    continue

                # compute and update the dominant container
                dom_containers = _dominant_container(
                                            target.containers.get(target_arg, None),
                                            dom_containers
                                            )

        return dom_containers

    ############################################################################
    def assign_input_index(self, var, index):
        """reassigns the index for this variable in the process argument list"""
        # reset the input index to a new one
        self._inputs[var].set_index(index)
        self.update()

    ############################################################################
    def debug_serialization(self):
        """helper function to debug what part of a block is not serializable"""
        # NOTE: needs to be updated to use dill's builtin debugging tools
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
                    dill.dumps(val)
                except Exception as e:
                    self.logger.error("error serializing {}.{}: {}".format(block,key,e))
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
        self.logger = get_logger(self.id, pipeline=self)
        # log the new name
        self.logger.warning("renamed from '%s' to '%s'" % (old_name, self.name))
        return self


    ############################################################################
    #                               magic
    ############################################################################
    def __call__(self, *pos_data, fetch=None, skip_enforcement=False, **kwdata):
        """aliases self.process with same signature for more natural use"""
        return self.process(*pos_data, fetch=None, skip_enforcement=False,
                                                   **kwdata)

    ############################################################################
    # COPYING & PICKLING
    def __getstate__(self):
        return self.__dict__

    ############################################################################
    def __setstate__(self, state):
        """resets the uuid in the event of a copy"""
        state['uuid'] = uuid4().hex
        self.__dict__.update(state)
        # updates the logger for the new state
        self.logger = get_logger(self.id, pipeline=self)

    ############################################################################
    def __del__(self):
        """deletes pipeline and sends a delete message to the dashboard"""
        # self.__send_delete_msg_to_dash()

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

    ############################################################################
    @property
    def variables(self):
        """:obj:`list` of :obj:`str`: all variables in the pipeline"""
        return list( self.vars.keys() )

    ############################################################################
    @property
    def types(self):
        """(obj:`dict` of str : type): the types compatible for input arguments.
        This is computed dynamically so it will automatically reflect changes to
        Blocks"""
        # Iterate through pipeline args and compute the dominant type
        types = {}
        for pype_arg in self.args:
            arg_types = self.get_types_for(pype_arg)
            types[pype_arg] = arg_types
            # check if there is at least 1 valid type
            if not (arg_types is None):
                if len(arg_types) == 0:
                    # log it, but don't throw an error
                    msg = "no valid types found for {}".format(pype_arg)
                    self.logger.error(msg)

        return types

    ############################################################################
    @property
    def shapes(self):
        """(obj:`dict` of str : tuple): the shapes compatible for input
        arguments. This is computed dynamically so it will automatically reflect
        changes to Blocks"""
        # Iterate through pipeline args and compute the dominant shapes
        shapes = {}
        for pype_arg in self.args:
            arg_shapes = self.get_shapes_for(pype_arg)
            shapes[pype_arg] = arg_shapes
            # check if there is at least 1 valid type
            if not (arg_shapes is None):
                if len(arg_shapes) == 0:
                    # log it, but don't throw an error
                    msg = "no valid shapes found for {}".format(pype_arg)
                    self.logger.error(msg)

        return shapes

    ############################################################################
    @property
    def containers(self):
        """(obj:`dict` of str : container): the containers compatible for input
        arguments. This is computed dynamically so it will automatically reflect
        changes to Blocks"""
        # Iterate through pipeline args and compute the dominant container
        containers = {}
        for pype_arg in self.args:
            arg_containers = self.get_containers_for(pype_arg)
            containers[pype_arg] = arg_containers
            # check if there is at least 1 valid container
            if not (arg_containers is None):
                if len(arg_containers) == 0:
                    # log it, but don't throw an error
                    msg = "no valid containers found for {}".format(pype_arg)
                    self.logger.error(msg)

        return containers

    ############################################################################
    @property
    def void_vars(self):
        """set: unordered set of variables which won't have data assigned to them
            during runtime"""
        void_vars = set()
        for node,attrs in self.graph.nodes(data=True):
            # if the block is void (has no outputs), then we add the variable names to a set
            if attrs['block'].void:
                void_vars.update(attrs['outputs'])

        return void_vars

    ############################################################################
    @property
    def noncomputable(self):
        """set: unordered set of every variable that can't be computed because
            it relies on void data"""
        noncomputable = set()
        for var in self.void_vars:
            noncomputable.update( self.get_successors(var) )
        return noncomputable
