# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018 - 2020 Jeff Maggio, Jai Mehra, Ryan Hartzell

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
from .Logger import MASTER_LOGGER, get_logger, ImagepypelinesLogger, set_log_level, get_master_logger
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


def add_plugin(plugin_name, plugin_module, add_to_namespace=True):
    """adds the given plugin to ImagePypelines

    Args:
        plugin_name(str): the name of the desired plugin namespace
        plugin_module(module): the valid module object for the plugin
        add_to_namespace(bool): whether or not to add the plugin to the
            ImagePypelines namespace so it's available as `ip.plugin_name`.
            If False, then you will only be access your plugin namespace using
            `ip.get_plugin_by_name`. Defaults to True.

    Returns:
        None
    """
    import sys
    ip_module = sys.modules[__name__]
    get_master_logger().debug(
        "loading plugin '{0}' - it will be available as imagepypelines.{0}"\
        .format(plugin_name))

    if add_to_namespace:
        # add the plugin to the current namespace
        setattr(ip_module, plugin_name, plugin_module)

    # update the default shape functions if the plugin provides new ones
    SHAPE_FUNCS.update( getattr(plugin_module, 'SHAPE_FUNCS', {}) )

    # update the default homogenus containers if the plugin provides new ones
    HOMOGENUS_CONTAINERS.extend( getattr(plugin_module, 'HOMOGENUS_CONTAINERS', []) )

    # add the plugin name to a global list for debugging
    LOADED_PLUGINS[plugin_name] = plugin_module

# define a function to load all the plugins so it's easier to keep the namespace
# clean
def load_plugins():
    """Load all installed plugins to the imagepypelines namespace"""
    # import these again in case this function is called multiple times and it's
    # deleted from the global namespace
    import pkg_resources
    # load in all installed python packages with our plugin entry_point
    required_objects = []
    plugins = {
                entry_point.name: entry_point.load()
                for entry_point
                in pkg_resources.iter_entry_points('imagepypelines.plugins')
                }

    for plugin_name in sorted( plugins.keys() ):
        plugin_module = plugins[plugin_name]
        add_plugin(plugin_name, plugin_module, True)

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


def get_plugin_by_name(plugin_name):
    """fetches the plugin module using its name"""
    require(plugin_name)
    return LOADED_PLUGINS[plugin_name]


# ---------- delete namespace pollutants ----------
del pkg_resources, os, uuid4, time, OrderedDict, sys
