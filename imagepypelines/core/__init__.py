# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018 Jeff Maggio, Nathan Dileas, Ryan Hartzell

# constants.py
from .constants import *

# BaseBlock.py
from .BaseBlock import ArrayType
from .BaseBlock import IoMap
from .BaseBlock import BaseBlock

# block_subclasses.py
from .block_subclasses import SimpleBlock
from .block_subclasses import BatchBlock
from .block_subclasses import TfBlock

# caching.py
from .caching import make_cache
from .caching import Cache
# JM: create builtin caches
make_cache('tmp',
		'Temporary Cache intended for short-term temporary use'\
		+ ' (memory management)')
make_cache('metadata',
		'Persistent Cache intended for use by data in use between'\
		 + ' imagepypelines sessions')
make_cache('datasets',
		'Persistent Cache intended exclusively to store datasets downloaded'\
		 + ' using a webcrawler')

# error_checking.py
from .error_checking import interpolation_type_check
from .error_checking import dtype_type_check
from .error_checking import is_numpy_array
from .error_checking import is_iterable
from .error_checking import type_error_message

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

# filters.py
from .filters import low_pass
from .filters import high_pass

# img_tools.py
from .img_tools import normalize_and_bin
from .img_tools import quick_image_view
from .img_tools import number_image
from .img_tools import centroid
from .img_tools import frame_size
from .img_tools import dimensions
from .img_tools import norm_01
from .img_tools import norm_ab
from .img_tools import norm_dtype

# imports.py
from .imports import import_tensorflow
from .imports import import_opencv

# ml_tools.py
from .ml_tools import accuracy
from .ml_tools import confidence_99
from .ml_tools import confidence_95
from .ml_tools import confidence_90
from .ml_tools import confidence
from .ml_tools import batch
from .ml_tools import batches_to_list
from .ml_tools import sample

# pipeline_tools.py
from .pipeline_tools import quick_block

# Pipeline.py
from .Pipeline import restore_from_file
from .Pipeline import restore_from_pickle
from .Pipeline import Pipeline

# Printer.py
from .Printer import get_printer
from .Printer import disable_all_printers
from .Printer import whitelist_printer
from .Printer import blacklist_printer
from .Printer import reset_printer_lists
from .Printer import disable_printout_colors
from .Printer import enable_printout_colors
from .Printer import get_active_printers
from .Printer import set_global_printout_level
from .Printer import get_default_printer
from .Printer import debug
from .Printer import info
from .Printer import warning
from .Printer import error
from .Printer import critical
from .Printer import comment
from .Printer import Printer

# quick_types.py
from .quick_types import RGB
from .quick_types import GRAY

# standard_image.py
from .standard_image import STANDARD_IMAGES
from .standard_image import list_standard_images
from .standard_image import standard_image_filenames
from .standard_image import standard_image_gen
from .standard_image import list_standard_images
from .standard_image import standard_images
from .standard_image import funcs

import sys

curr_module = sys.modules[__name__]
for img_name in STANDARD_IMAGES.keys():
	setattr(curr_module, img_name, getattr(funcs, img_name))

# ND 9/7/18 - delete these so that the imagepypelines namespace is not polluted
del sys, curr_module, funcs, STANDARD_IMAGES

# Viewer.py
from .Viewer import Viewer

# import submodules
from . import util
from . import io
from . import ml
