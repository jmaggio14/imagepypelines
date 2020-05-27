# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018-2020 Jeff Maggio, Ryan Hartzell, and collaborators

# arg_checking.py
from .arg_checking import DEFAULT_SHAPE_FUNCS

# constants.py
from .constants import *

# Block.py
from .Block import Block

# Data.py
from .Data import Data

# block_subclasses.py
# create a namespace to store FuncBlocks in so they can be pickled
import types
func_namespace_doc = \
"""
This is a holding module for functions that are used in Blocks created by
the blockify decorator or FuncBlock object. Objects are stored here so they can
serialize by the pickle module
"""
func_namespace = types.ModuleType('func_namespace',
                                        func_namespace_doc )
del types, func_namespace_doc

# block_subclasses imports
from .block_subclasses import FuncBlock
from .block_subclasses import Input
from .block_subclasses import Leaf
from .block_subclasses import PipelineBlock

# Exceptions.py
from .Exceptions import PipelineError
from .Exceptions import BlockError

# imports.py
# from .imports import import_tensorflow
# from .imports import import_opencv

# io_tools.py
from .io_tools import passgen
from .io_tools import prevent_overwrite
from .io_tools import make_numbered_prefix
# from .io_tools import convert_to

# from .io_tools import CameraCapture
# from .io_tools import Emailer
# from .io_tools import ImageWriter

# ml_tools.py
# from .ml_tools import accuracy
# from .ml_tools import confidence_99
# from .ml_tools import confidence_95
# from .ml_tools import confidence_90
# from .ml_tools import confidence
# from .ml_tools import chunk
# from .ml_tools import batch
# from .ml_tools import chunks2list
# from .ml_tools import xsample
# from .ml_tools import xysample
# from .ml_tools import ConfigFactory
# from .ml_tools import Mnist
# from .ml_tools import MnistFashion
# from .ml_tools import Cifar10
# from .ml_tools import Cifar100


# pipeline_tools.py
from .pipeline_tools import blockify

# Pipeline.py
from .Pipeline import Pipeline
from .Pipeline import Input


# util.py
# from .util import print_args
from .util import arrsummary
from .util import timer
from .util import timer_ms
from .util import Timer
