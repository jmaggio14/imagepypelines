# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018-2019 Jeff Maggio, Nathan Dileas, Ryan Hartzell

# -------- setup a uuid for this imagepypelines session -------
import time
from uuid import uuid4
import os
import pkg_resources

init_time = time.time()
"""unix time initiatization time for this imagepypelines session"""
session_uuid = uuid4().hex
"""a universally unique id for this imagepypelines session"""

# --------- retrieve the source directory for our standard images ---------
STANDARD_IMAGE_DIRECTORY = pkg_resources.resource_filename(__name__,
                                                        'data/standard_images')
"""the location where imagepypelines standard images are stored"""
# -------- define the cache directory for this machine and session -------
CACHE = os.path.join(os.path.expanduser('~'),'.imagepypelines')
"""the local imagepypelines cache/config directory for this user"""

# ---------- delete namespace pollutants ----------
del pkg_resources, os, uuid4, time

# ----------- Setup the Root ImagePypelines Logger ---------------
# constants our users can modify to change color behavior
# import the master logger
from .Logger import MASTER_LOGGER, get_logger, IpLogger
# import master logger convienence function
from .Logger import debug, info, warning, error, critical


# ---------- import imagepypelines ----------
from .version_info import *
from .core import *
from . import builtin_blocks as blocks
from . import builtin_pipelines as pipelines
