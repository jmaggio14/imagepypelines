# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018 Jeff Maggio, Nathan Dileas, Ryan Hartzell

import pkg_resources
# retrieve the source directory for our standard images
STANDARD_IMAGE_DIRECTORY = pkg_resources.resource_filename(__name__,
                                                        'data/standard_images')

# setup a cache on the local machine
import os
home = os.path.expanduser('~')
CACHE_PATH = os.path.join(home,'.imagepypelines')
CACHE_TMP = os.path.join(CACHE_PATH,'tmp')
CACHE_BLOCK_META = os.path.join(CACHE_PATH,'block_metadata')
CACHE_DATASETS = os.path.join(CACHE_PATH,'datasets')

if not os.path.exists(CACHE_PATH):



del pkg_resources # delete namespace pollutants


from .version_info import *
from .core import *
from . import builtin_blocks as blocks
from . import builtin_pipelines as pipelines
