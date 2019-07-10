# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018-2019 Jeff Maggio, Nathan Dileas, Ryan Hartzell

# constants.py
from .constants import *

# BaseBlock.py
from .BaseBlock import ArrayType
from .BaseBlock import Same
from .BaseBlock import Incompatible
from .BaseBlock import IoMap
from .BaseBlock import BaseBlock

# block_subclasses.py
from .block_subclasses import SimpleBlock
from .block_subclasses import BatchBlock
# from .block_subclasses import TfBlock

# caching.py
from .caching import Cache
cache = Cache() # instantiate the cache
del Cache

# Exceptions.py
from .Exceptions import CameraReadError
from .Exceptions import InvalidInterpolationType
from .Exceptions import InvalidNumpyType
from .Exceptions import CrackedPipeline
from .Exceptions import BlockRequiresLabels
from .Exceptions import IncompatibleTypes
from .Exceptions import InvalidBlockInputData
from .Exceptions import InvalidBlockInputLabels
from .Exceptions import InvalidProcessStrategy
from .Exceptions import InvalidLabelStrategy
from .Exceptions import DataLabelMismatch
from .Exceptions import PluginError
from .Exceptions import CachingError
from .Exceptions import ChecksumError

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

# imports.py
from .imports import import_tensorflow
from .imports import import_opencv

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

# pipeline_tools.py
from .pipeline_tools import quick_block

# Pipeline.py
from .Pipeline import Pipeline

# quick_types.py
from .quick_types import *

# standard_image.py
from .standard_image import STANDARD_IMAGES
from .standard_image import list_standard_images
from .standard_image import standard_image_filenames
from .standard_image import standard_image_gen
from .standard_image import list_standard_images
from .standard_image import standard_images
from .standard_image import get_standard_image

from .standard_image import funcs
import sys

curr_module = sys.modules[__name__]
for img_name in STANDARD_IMAGES.keys():
	setattr(curr_module, img_name, getattr(funcs, img_name))

# ND 9/7/18 - delete these so that the imagepypelines namespace is not polluted
del sys, curr_module, funcs, STANDARD_IMAGES

# util.py
from .util import interpolation_type_check
from .util import dtype_type_check
from .util import print_args
from .util import arrsummary
from .util import function_timer
from .util import function_timer_ms
from .util import Timer

# Viewer.py
from .Viewer import Viewer

# import submodules
from . import io
from . import ml
