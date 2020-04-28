# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018-2020 Jeff Maggio, Ryan Hartzell, and collaborators

# -------- setup a uuid for this imagepypelines session -------
import time
from uuid import uuid4
import os
import pkg_resources
import sys

init_time = time.time()
"""unix time initiatization time for this imagepypelines session"""
session_uuid = uuid4().hex
"""a universally unique id for this imagepypelines session"""

# ----------- Setup the Root ImagePypelines Logger ---------------
# import the master logger
from .Logger import MASTER_LOGGER, get_logger, ImagepypelinesLogger, set_log_level
# import master logger convienence function
# NOTE: import logging constants our users can modify to change color behavior


# ---------- import imagepypelines ----------
from .version_info import *
from .core import *

# ---------- import plugins ----------
from collections import OrderedDict
LOADED_PLUGINS = OrderedDict()
"""module level OrderedDict that contains the all loaded modules in the order in
which they were loaded"""


# define a function to load all the plugins so it's easier to keep the namespace
# clean
def load_plugins():
    """Load all installed plugins to the imagepypelines namespace"""
    # load in all installed python packages with our plugin entry_point
    required_objects = []
    plugins = {
                entry_point.name: entry_point.load()
                for entry_point
                in pkg_resources.iter_entry_points('imagepypelines.plugins')
                }

    for plugin_name in sorted( plugins.keys() ):
        ip_module = sys.modules[__name__]
        plugin_module = plugins[plugin_name]

        # JM - commented out 04/11/20
        # # check that the module has the required objects
        # for req in required_objects:
        #     if not hasattr(plugin_module, req):
        #         raise PluginError(
        #                 "Plugin '%s' doesn't meet requirements" % plugin_name)
        #     elif not callable( getattr(plugin_module, req) ):
        #         raise PluginError(
        #                 "Plugin '%s' doesn't meet requirements" % plugin_name)

        MASTER_LOGGER.info(
            "loading plugin '{0}' - it will be available as imagepypelines.{0}"\
            .format(plugin_name))

        # add the plugin to the current namespace
        setattr(ip_module, plugin_name, plugin_module)

        # add the plugin name to a global list for debugging
        LOADED_PLUGINS[plugin_name] = plugin_module


# load all of our plugins
load_plugins()

# define a function to check if a plugin is loaded
def require(plugin_name):
    """check to make sure the given plugin is loaded and raise an error if it
    is not in the imagepypelines namespace
    """
    import sys

    if not plugin_name in LOADED_PLUGINS.keys():
        raise RuntimeError('unable to find required plugin "%s"' % plugin_name)

# ---------- delete namespace pollutants ----------
del pkg_resources, os, uuid4, time, OrderedDict, sys
