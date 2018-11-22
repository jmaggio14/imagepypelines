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

# -------- setup a cache on the local machine -------
import os
home = os.path.expanduser('~')
CACHE = os.path.join(home,'.imagepypelines')
CACHE_TMP = os.path.join(CACHE,'tmp')
CACHE_META = os.path.join(CACHE,'metadata')
CACHE_DATASETS = os.path.join(CACHE,'datasets')

# making cache directories
for subdir in [CACHE_TMP,CACHE_META,CACHE_DATASETS]:
    if not os.path.exists(subdir):
        os.makedirs(subdir)


# ---------- delete namespace pollutants ----------
del pkg_resources, os
del home, subdir


# ---------- import imagepypelines ----------
from .version_info import *
from .core import *
from . import builtin_blocks as blocks
from . import builtin_pipelines as pipelines


# --------- purge data stored in the ~/.imagepypelines/tmp directory
# --------- presumably, this was from the last session
tmp.purge()
