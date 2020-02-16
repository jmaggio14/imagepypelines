# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018-2019 Jeff Maggio, Nathan Dileas, Ryan Hartzell
from ..Logger import get_logger
from ..Logger import ImagepypelinesLogger
from .Exceptions import InvalidBlockInputData
from .Exceptions import InvalidProcessStrategy
from .Exceptions import InvalidLabelStrategy
from .Exceptions import DataLabelMismatch
from .Exceptions import BlockRequiresLabels
from .Exceptions import IncompatibleTypes
from .constants import NUMPY_TYPES

import copy
import time
from uuid import uuid4
from abc import ABCMeta, abstractmethod
import inspect

import networkx as nx
#
#
# class ArrayType(object):
#     """Object to describe the shapes of Arrays for Block inputs or outputs
#
#     Object that contains the shapes and datatypes of an input or output
#     for a BaseBlock
#
#     Args:
#         *array_shapes(vargs of array shapes): acceptable shapes. Arbitrary
#             length axes can be represented by None.
#             example: [None,None,3] (for rgb image)
#     """
#
#     def __init__(self, *array_shapes):
#         if len(array_shapes) > 0:
#             # -------------------- error-checking ---------------------
#             if not all(isinstance(shape, (tuple, list)) for shape in array_shapes):
#                 raise TypeError("all array shapes must be tuples or lists")
#
#             # ensure that every element is a positive integer or NoneType
#             shapes = list(list(shp) for shp in array_shapes)
#             for shp in shapes:
#                 for i in range(len(shp)):
#                     if isinstance(shp[i], (float, int)):
#                         assert shp[i] > 0, "elements of shape must be > 0 or None"
#                         shp[i] = int(shp[i])
#
#                     elif not (shp[i] is None):
#                         error_msg = "all elements must be positive integers or None"
#                         raise ValueError(error_msg)
#
#             # -------------------- create instance variables ---------------------
#             self.shapes = tuple(tuple(shp) for shp in shapes)
#
#         else:
#             self.shapes = ()
#
#         self.arbitrary = not bool(len(self.shapes))
#
#     def __str__(self):
#         if len(self.shapes) == 0:
#             return "ArrayType(<arbitrary shape>)"
#         else:
#             return "ArrayType({})".format(', '.join(str(s) for s in self.shapes))
#
#     def __repr__(self):
#         return str(self)
#
#     def __eq__(self, other):
#         if isinstance(other, ArrayType):
#             return hash(self) == hash(other)
#         return False
#
#     def __hash__(self):
#         # NOTE(Jeff Maggio) - possible issue here because tuples aren't sorted
#         clean = lambda shp: tuple((-1 if ele is None else ele) for ele in shp)
#         sortable = (clean(shp) for shp in self.shapes)
#         return hash(tuple(sorted(sortable)))
#
#
# class Same(object):
#     """class meant to be the output in an IoMap.
#     Indicates that the output is the same as the input is returned"""
#     pass
#
#
# class Incompatible(object):
#     def __str__(self):
#         return "No known outputs due to incompatible Inputs"
#
#     def __repr__(self):
#         return str(self)
#
#
# class IoMap(tuple):
#     """mapping object to determine the output of block
#     IoMaps are used to predict the output of a block given a certain type of
#     input. Every block contains an IoMap located under block.io_map
#     Args:
#         io_map(dict,IoMap): dictionary that describes the input outputs of the
#             block. Of the form: io_map[input_type] = output_type
#     Attributes:
#         non_arrays(tuple): mapping of non-array input-outputs for this io_map
#         arrays(tuple): mapping of array input-outputs for this io_map
#         inputs(tuple): tuple of inputs for this io map
#         outputs(tuple): tuple of outputs for this io map
#     """
#     def __new__(cls, io_map):
#         # -------------- ERROR CHECKING -----------------------
#         if isinstance(io_map, IoMap):
#             return io_map
#         elif isinstance(io_map, dict):
#             io_map = io_map.items()
#         elif not isinstance(io_map, tuple):
#             raise TypeError(
#                 "IoMap must be instantiated with a dictionary, tuple, or other IoMap, not %s"
#                 % type(io_map))
#
#         # ---------------- Breaking dictionary up into a mapping --------------
#         # {key1:val1,key2:val2} --> ( (key1,val1),(key2,val2) )
#         # splitting apart all Array Types with multiple shapes
#         # ArrayType(shape1,shape2) --> ArrayType(shape1), ArrayType(shape2)
#         # going through inputs first
#         reduced_io_map = []
#         for i, o in io_map:
#             reduced_io_map.extend(cls.reduce(i, o))
#
#         # return the new reduced mapping
#         return super(IoMap, cls).__new__(cls, tuple(set(reduced_io_map)))
#
#     def __init__(self, io_map):
#         self.non_arrays = tuple((i, o) for i, o in self if (not isinstance(i, ArrayType)))
#         self.arrays = tuple((i, o) for i, o in self if isinstance(i, ArrayType))
#
#         self.inputs = tuple(i for i, o in self)
#         self.outputs = tuple(o for i, o in self)
#
#     @staticmethod
#     def reduce(i, o):
#         """reduces ArrayTypes with multiple shapes to multiple single
#         shape ArrayTypes
#         ArrayType(shape1,shape2) --> ArrayType(shape1), ArrayType(shape2)
#         Args:
#             i (ArrayType): block input
#             o (ArrayType): block output
#         Returns:
#             tuple: mapping of reduced types ((i1,o1),(i2,o2)...)
#         """
#         if not isinstance(i, ArrayType):
#             reduced_i = ((i, o), )
#         else:
#             if i.arbitrary:
#                 split = (ArrayType(),)
#             else:
#                 split = tuple(ArrayType(shp) for shp in i.shapes)
#             reduced_i = zip(split, (o,)*len(split))
#
#         reduced = []
#         for i, o in reduced_i:
#             if not isinstance(o, ArrayType):
#                 reduced.append((i, o))
#             else:
#                 if o.arbitrary:
#                     split = (ArrayType(),)
#                 else:
#                     split = tuple(ArrayType(shp) for shp in o.shapes)
#                 reduced.extend(zip((i,)*len(split), split))
#
#         return tuple(reduced)
#
#     @staticmethod
#     def shape_comparison(input_array, acceptable_array):
#         """compares ArrayType shapes and returns a boolean to indicate
#         compatability
#         Args:
#             input_array(tuple): input ArrayType
#             acceptable_array(tuple): acceptable ArrayTypes
#         Returns:
#             compatible(bool): whether or the input shape is compatible with
#                 this block
#         """
#         # if the acceptable array has an arbitrary shape, then it's compatible
#         # no matter what
#         if acceptable_array.arbitrary:
#             return True
#
#         input_shape = input_array.shapes[0]
#         acceptable_shape = acceptable_array.shapes[0]
#
#         # if they have a different number of axis, they aren't compatible
#         if len(input_shape) != len(acceptable_shape):
#             return False
#
#         # compare every element
#         compatible_by_axis = []
#         for input_i, acceptable_i in zip(input_shape, acceptable_shape):
#             # if block element is None, then arbitrary length for this axis is accepted
#             # so no more comparisons are needed for this element
#             if (acceptable_i == None) or (input_i == acceptable_i):
#                 compatible_by_axis.append(True)
#             else:
#                 compatible_by_axis.append(False)
#
#         return all(compatible_by_axis)
#
#     def output(self, input_types):
#         """gets the given output(s) of this IoMap given a input type or types
#         Args:
#             input_types(tuple,set): tuple or set of input types
#         Returns:
#             outputs(set): tuple of output types this block produces given the
#                 input_types
#         """
#         outputs = set()
#
#         for input_type in input_types:
#             # Quick Check for direct matches
#             if input_type in self.inputs:
#                 indices = [idx for idx, it in enumerate(self.inputs) if (it == input_type)]
#                 for idx in indices:
#                     out = self.outputs[idx]
#                     if isinstance(out, Same):
#                         outputs.add(self.inputs[idx])
#                     else:
#                         outputs.add(out)
#
#             elif isinstance(input_type, ArrayType):
#                 for arr_in, arr_out in self.arrays:
#                     if self.shape_comparison(input_type, arr_in):
#                         if isinstance(arr_out, Same):
#                             outputs.add(arr_in)
#                         else:
#                             outputs.add(arr_out)
#
#             else:
#                 raise IncompatibleTypes("invalid input type, must be"
#                      + "({}) not {}".format(self.inputs, input_type))
#
#             return tuple(outputs)
#
#     def __str__(self):
#         return repr(self)
#
#     def __repr__(self):
#         # create a 'readable' io map that simply replaces outputs defined as 'Same'
#         # with it's corresponding input
#         # (ArrayType((512,512)),Same)-->(ArrayType((512,512)),ArrayType((512,512)))
#         io = []
#         for i, o in self:
#             if isinstance(o, Same) and isinstance(i, ArrayType):
#                 o = str(i) + " [same shape as input]"
#             io.append((i, o))
#
#         io_map_str = "\n".join("{} --> {}".format(i, o) for i, o in io)
#         return io_map_str
#
#     # def __reduce__(self):
#     #     """make io maps copyable and serializable"""
#     #     constructor = IoMap
#     #     args = tuple( (i,o) for i,o in self )
#     #     return constructor, args
#

def describe_block(block, notes):
    if notes is None:
        notes = "<no description provided by the author>"

    io_map_str = repr(block.io_map)
    description = \
"""{name}

{notes}

io mapping:
{io_map}""".format(name=block.name, notes=notes, io_map=io_map_str)

    return description

# VERY BAREBONES IMPLEMENTATION OF BASEBLOCK!!! It is a sufficient proof of concept and I believe is fully extendable
# class BaseBlock(object):
#
#     def __init__(self, name, inputs=None, outputs=None):
#
#         self.id = uuid4().hex
#         self.user_name = f"{name}_{self.id[:6]}"
#
#         if inputs is None:
#             inputs = {}
#
#         if outputs is None:
#             outputs = {}
#
#         # these should be set via provided functions or directly by user
#         self._inputs = inputs
#         self._outputs = ouptuts
#
#     def __str__(self):
#
#         return f"This Block's name is < {self.user_name} >"
#
#     def __repr__(self):
#
#         """
#         This representation is what is used as the hashable key for the instance
#             in networkx graphs. Effectively, the instance is stored, but looked
#             up and identified via its repr string.
#         """
#
#         # I'll change every instance of user_name to the more appropriate block/pipeline/logger id, but for now this works as a POC
#         return self.user_name
#
#     @property
#     def inputs(self):
#
#         return self._inputs
#
#     @property
#     def outputs(self):
#
#         return self._outputs
#
#     def process(self):
#
#         print(f"<{self.user_name}>'s inputs are resolved, processing them, adding to output dictionary...")

class BaseBlock(object):
    """BaseBlock object which is the root class for SimpleBlock and BatchBlock
    subclasses

    This is the building block (pun intended) for the entire imagepypelines
    pipelining system. All blocks, both SimpleBlocks and BatchBlocks, will
    inherit from this object. Which contains base functionality to setup a
    block's loggers, unique name, standard input/output_shapes and special
    functions for pipeline objects to call

    Args:
        io_map(IoMap,dict): dictionary of input-output mappings for this
            Block
        name(str): name for this block, it will be automatically created/modified
            to make sure it is unique
        notes(str): a short description of this block
        requires_training(bool): whether or not this block will require
            training
        requires_labels(bool): whether or not this block will require
            labels during training

    Attributes:
        io_map(IoMap): object that maps inputs to this block to it's outputs.
            subclass of tuple where I/O is stored as:
            ( (input1,output1),(input2,output2)... )
        name(str): unique name for this block
        n_inputs(int): number of data inputs to block (len of data input INCLUDING TRAIN DATA ***TENTATIVE CHANGE USING **kwargs DICT IN PROCESS AND TRAIN AS A INSTANCE VARIABLE!!!: RYAN)
        n_outputs(int): number of data outputs to block (len of data output)
        inputs(dict): key names of input data corresponding to each index in data
        outputs(dict): key names of output data corresponding to each index in return tuple
        notes(str): a short description of this block, what operations it
            performs, etc. This will be included in the blocks 'description'
        requires_training(bool): whether or not this block will require
            training
        trained(bool): whether or not this block has been trained, True
            by default if requires_training = False
        logger(ip.ImagepypelinesLogger): logger for this block,
            registered to 'name'
        description(str): a readable description of this block that includes
            user defined notes and a summary of inputs and outputs
    """
    __metaclass__ = ABCMeta
    def __init__(self,name=None):
        # setup absolutely unique id for this block
        # this will change even if the block is copied or pickled
        self.uuid = name + '-' + uuid4().hex if name is not None else self.__class__.__name__ + '-' + uuid4().hex
        # ----------- building a unique name for this block ------------
        # logger_name is set up as follows
        # <readable_name>-<sibling_id>-<uuid>
        if name is None:
            name = self.__class__.__name__
        logger_name = self.__get_logger_name(name,self.uuid)

        # ------ setting up instance variables
        self.name = name
        self.logger_name = logger_name

        # this will be defined in _pipeline_pair
        self.logger = None

        # setup initial tags
        self.tags = set()

        # whether or not the input names have been defined for this block
        self._arg_spec = None

        super(BaseBlock,self).__init__()

    def _pipeline_process(self, *data):
        return self.process_strategy(*data)

    @abstractmethod
    def process_strategy(self, *data):
        """overarching processing management function for this block

        Args:
            data(list): list of datums to process

        Returns:
            list: processed datums
        """
        raise NotImplementedError(
            "'process_strategy' must be overloaded in all children")

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)

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
        return "{0} #{0}-{1}".format(basename,uuid[-6:])

    @abstractmethod
    def inputs(self):
        pass

    def get_default_node_attrs(self):
        attrs = { 'name':self.name,
                    'type':type(self),
                    }
        return attrs






# # END
