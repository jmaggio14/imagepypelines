# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018-2020 Jeff Maggio, Ryan Hartzell, and collaborators
#
from .Pipeline import Pipeline
from .block_subclasses import FuncBlock
from ..Logger import error as iperror

import numpy as np
import networkx as nx
from math import sqrt, atan2, degrees

ROOT_COLOR = 'red'
ROOT_SHAPE = 'p'
ROOT_SIZE = 1200
ROOT_OUTEDGE_COLOR = 'red'

BRANCH_COLOR = 'orange'
BRANCH_SHAPE = 's'
BRANCH_SIZE = 1200
BRANCH_OUTEDGE_COLOR = 'black'

LEAF_COLOR = 'green' # (duh)
LEAF_SHAPE = 'o'
LEAF_SIZE = 400

DATA_COLOR = LEAF_COLOR
DATA_SHAPE = LEAF_SHAPE
DATA_TEXT = 10
DATA_SIZE = LEAF_SIZE
EDGE_ARROW_STYLE = "Simple,tail_width=0.5,head_width=4,head_length=8"

################################################################################
def blockify(kwargs={},
                batch_size="each",
                types=None,
                shapes=None,
                containers=None):
    """decorator which converts a normal function into a un-trainable
    block which can be added to a pipeline. The function can still be used
    as normal after blockification (the __call__ method is setup such that
    unfettered access to the function is permitted)

    Args:
        **kwargs: hardcode keyword arguments for a function, these arguments
            will not have to be used to. defaults to {}
        types(:obj:`dict`,None): Dictionary of input types. If arg doesn't
            exist as a key, or if the value is None, then no checking is
            done. If not provided, then will default to args as keys, None
            as values.
        shapes(:obj:`dict`,None): Dictionary of input shapes. If arg doesn't
            exist as a key, or if the value is None, then no checking is
            done. If not provided, then will default to args as keys, None
            as values.
        containers(:obj:`dict`,None): Dictionary of input containers. If arg
            doesn't exist as a key, or if the value is None, then no
            checking is done. If not provided, then will default to args as
            keys, None as values.
            *if batch_size is "each", then the container is irrelevant and can
            be safely ignored!*
        batch_size(str, int): the size of the batch fed into your process
            function. Must be an integer, "all", or "each". defaults to Each

    Example:
        >>> import imagepypelines as ip
        >>>
        >>> @ip.blockify( kwargs=dict(value=10) )
        >>> def add_value(datum, value):
        ...    return datum + value
        >>>
        >>> type(add_value)
        <class 'FuncBlock'>



    """
    def _blockify(func):
        return FuncBlock(func,
                        kwargs,
                        batch_size=batch_size,
                        types=types,
                        shapes=shapes,
                        containers=containers)
    return _blockify

################################################################################
# def to_json(pipeline, pickle_protocol=pickle.HIGHEST_PROTOCOL):
#     return pipeline.to_json(pickle_protocol)
#
# ################################################################################
# def from_json(jsonified):
#     return Pipeline.from_json(jsonified)

################################################################################
def debug_pickle(pipeline):
    return pipeline.debug_pickle()

################################################################################
