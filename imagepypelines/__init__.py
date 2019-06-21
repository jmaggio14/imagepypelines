# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018-2019 Jeff Maggio, Nathan Dileas, Ryan Hartzell

# -------- setup a uuid for this imagepypelines session -------
import time
from uuid import uuid4
init_time = time.time()
"""initiatization time for this imagepypelines session"""
session_uuid = uuid4().hex
"""a universally unique id for this imagepypelines session"""

# --------- enable terminal colors if we are in on a windows system ---------
import os
if os.name == 'nt':
    import colorama
    colorama.init()
    del colorama

# --------- retrieve the source directory for our standard images ---------
import pkg_resources
STANDARD_IMAGE_DIRECTORY = pkg_resources.resource_filename(__name__,
                                                        'data/standard_images')
"""the location where imagepypelines standard images are stored"""
# -------- setup a cache directory on the local machine -------
CACHE = os.path.join(os.path.expanduser('~'),'.imagepypelines')
"""the local imagepypelines cache/config directory for this user"""

# ---------- delete namespace pollutants ----------
del pkg_resources, os, uuid4, time

# ---------- import imagepypelines ----------
from .version_info import *
from .core import *
from . import builtin_blocks as blocks
from . import builtin_pipelines as pipelines
