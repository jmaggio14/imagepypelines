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

# block_subclasses.py
from .block_subclasses import FuncBlock
from .block_subclasses import Input
from .block_subclasses import Leaf
from .block_subclasses import PipelineBlock

# caching.py
from .caching import Cache
cache = Cache() # instantiate the cache
del Cache

from .Exceptions import PipelineError
from .Exceptions import BlockError

# img_tools.py
from .img_tools import display_safe
from .img_tools import quick_image_view
from .img_tools import number_image
from .img_tools import centroid
from .img_tools import frame_size
from .img_tools import dimensions
from .img_tools import norm_01
from .img_tools import norm_ab
from .img_tools import norm_dtype
from .img_tools import low_pass
from .img_tools import high_pass
from .img_tools import Viewer

# imports.py
# from .imports import import_tensorflow
# from .imports import import_opencv

# io_tools.py
# --- standard imagery ---
from .io_tools import passgen
from .io_tools import list_standard_images
from .io_tools import standard_image_filenames
from .io_tools import standard_image_gen
from .io_tools import list_standard_images
from .io_tools import standard_images
from .io_tools import get_standard_image

from .io_tools import STANDARD_IMAGES
from .io_tools import funcs

import sys

curr_module = sys.modules[__name__]
for img_name in STANDARD_IMAGES.keys():
	setattr(curr_module, img_name, getattr(funcs, img_name))

# ND 9/7/18 - delete these so that the imagepypelines namespace is not polluted
del sys, curr_module, funcs, STANDARD_IMAGES

# --- other io ---
from .io_tools import prevent_overwrite
from .io_tools import make_numbered_prefix
from .io_tools import convert_to

# from .io_tools import CameraCapture
# from .io_tools import Emailer
# from .io_tools import ImageWriter

# ml_tools.py
from .ml_tools import accuracy
from .ml_tools import confidence_99
from .ml_tools import confidence_95
from .ml_tools import confidence_90
from .ml_tools import confidence
from .ml_tools import chunk
from .ml_tools import batch
from .ml_tools import chunks2list
from .ml_tools import xsample
from .ml_tools import xysample
from .ml_tools import ConfigFactory
from .ml_tools import Mnist
from .ml_tools import MnistFashion
from .ml_tools import Cifar10
from .ml_tools import Cifar100


# pipeline_tools.py
from .pipeline_tools import blockify
from .pipeline_tools import categorize_nodes
from .pipeline_tools import visualize

# Pipeline.py
from .Pipeline import Pipeline
from .Pipeline import Input


# util.py
from .util import interpolation_type_check
from .util import dtype_type_check
from .util import print_args
from .util import arrsummary
from .util import timer
from .util import timer_ms
from .util import Timer
