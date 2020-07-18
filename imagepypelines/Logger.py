# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018 - 2020 Jeff Maggio, Jai Mehra, Ryan Hartzell
#
import logging
from termcolor import colored
import sys

# --------- enable terminal colors if we are in on a windows system ---------
import os
if os.name == 'nt':
    import colorama
    colorama.init()
    del colorama


LOG_LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL,
    }
"""Log level strings mapped to their numerical values"""

LOG_COLORS = {
    'debug': 'cyan',
    'info': None,
    'warning': 'yellow',
    'error': 'red',
    'critical': 'red',
}
"""Module variable controlling the color of our logs, this can be modified to
suit the end user's needs or ignored entirely by setting
ip.MASTER_LOGGER.ENABLE_LOG_COLOR = False"""

LOG_TEXT_ATTRS = {
            'debug':['bold'],
            'info':None,
            'warning':['bold'],
            'error':None,
            'critical':['bold']
}
"""Module variable controlling the text attributes of our logs, this can be
modified to suit the end user's needs or ignored entirely by setting
ip.MASTER_LOGGER.ENABLE_LOG_COLOR = False"""

# this is defined lower down in this file
MASTER_LOGGER = None
"""logging.Logger subclass that is the root of all loggers instantiated in
ImagePypelines"""

# Define our new special Logger class that can be pickled
# (like the loggers of python 3.7)
class ImagepypelinesLogger( logging.getLoggerClass() ):
    """subclass of logging.Logger that can be pickled, also adds colored logging
    outputs if desired. the color, functionality and text attributes can be
    controlled by setting the module variables imagepypelines.LOG_COLORS,
    imagepypelines.ENABLE_LOG_COLOR, imagepypelines.LOG_TEXT_ATTRS

    Attributes:
        ENABLE_LOG_COLOR(bool): class level variable controlling whether or not
            to markup log output with ANSI color codes. True by default
    """
    ENABLE_LOG_COLOR = True
    def _color_msg(self, msg, level, LEVEL):
        if self.isEnabledFor(LEVEL) and self.ENABLE_LOG_COLOR:
            return colored(msg, LOG_COLORS[level], attrs=LOG_TEXT_ATTRS[level])
        return msg

    def debug(self, msg, *args, **kwargs):
        msg = self._color_msg(msg, 'debug', logging.DEBUG)
        return super().debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        msg = self._color_msg(msg, 'info', logging.INFO)
        return super().info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        msg = self._color_msg(msg, 'warning', logging.WARNING)
        return super().warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        msg = self._color_msg(msg, 'error', logging.ERROR)
        return super().error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        msg = self._color_msg(msg, 'critical', logging.CRITICAL)
        return super().critical(msg, *args, **kwargs)

    def getChild(self,*args,**kwargs):
        # make a formatter for the child logger
        child = super().getChild(*args,**kwargs)

        if not len(self.handlers):
            ch = logging.StreamHandler()
            formatter = logging.Formatter(
                                '%(asctime)s | %(name)s [ %(levelname)8s ]: %(message)s')
            ch.setFormatter(formatter)

            child.addHandler(ch)
        return child

    def setLevel(self, level, *args, **kwargs):
        level = LOG_LEVELS.get(level, level)
        super().setLevel(level, *args, **kwargs)

    # JEFF: modified from here https://github.com/python/cpython/blob/ca7b504a4d4c3a5fde1ee4607b9501c2bab6e743/Lib/logging/__init__.py
    def __reduce__(self):
        if self.name == 'ImagePypelines':
            return make_master, (self.level,)
        return logging.getLogger, (self.name,)

def get_master_logger():
    return make_master()

def make_master(level=logging.INFO):
    """creates the master logger if it doesn't exist, returns it if it does"""
    if MASTER_LOGGER:
        return MASTER_LOGGER

    # create our ImagePypelines master logger
    ch = logging.StreamHandler()
    formatter = logging.Formatter(
                        '%(asctime)s | %(name)s [ %(levelname)8s ]: %(message)s')
    ch.setFormatter(formatter)

    master = ImagepypelinesLogger('ImagePypelines')
    master.addHandler(ch)
    master.setLevel(level)

    # set our subclass as the root of all child loggers
    master.manager.setLoggerClass(ImagepypelinesLogger)
    return master

MASTER_LOGGER = make_master()

# function to create a new ImagePypelines Logger
def get_logger(name, log_level=logging.INFO):
    """Creates a new child logger of the ImagePypelines master logger, by
    default the new child logger has a log level of logging.INFO

    Args:
        name(str): the name of the new child logger
        log_level(int): the log level of the new logger, see python's logging
            module for more information

    Returns:
        ImagepypelinesLogger: a new child logger object from the ImagePypelines master
            logger
    """
    child = MASTER_LOGGER.getChild(name)
    return child


def set_log_level(log_level):
    """sets the global master logger level"""
    global MASTER_LOGGER
    log_level = LOG_LEVELS.get(log_level, log_level)
    MASTER_LOGGER.setLevel(log_level)

# END
