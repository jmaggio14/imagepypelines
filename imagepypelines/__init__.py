# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018-2019 Jeff Maggio, Nathan Dileas, Ryan Hartzell

import pkg_resources
# retrieve the source directory for our standard images
STANDARD_IMAGE_DIRECTORY = pkg_resources.resource_filename(__name__,
                                                        'data/standard_images')

# -------- setup a cache directory on the local machine -------
import os
CACHE = os.path.join(os.path.expanduser('~'),'.imagepypelines')

# ---------- delete namespace pollutants ----------
del pkg_resources, os


# ---------- import imagepypelines ----------
from .version_info import *
from .core import *
from . import builtin_blocks as blocks
from . import builtin_pipelines as pipelines
