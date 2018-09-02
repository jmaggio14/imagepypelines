"""
This file provides functions which will be used in the imsciutils
backend to print out messages
"""
from termcolor import colored
import os
# enabling colorama's ANSI code switcher if system is using windows
# so colored printouts will work
if os.name == 'nt':
    import colorama
    colorama.init()

COLORS = {
                'printmsg':'green',
                'debug':None,
                'info':None,
                'warning':'yellow',
                'error':'red',
                'critical': 'red',
                }

ATTRIBUTES = {
                    'printmsg':None,
                    'debug':None,
                    'info':None,
                    'warning':None,
                    'error':None,
                    'critical':['bold'],
                    }
ENABLE_COLOR = True

def disable_printout_colors():
    """disables colored printouts for imsciutils printout messages"""
    ENABLE_COLOR = False

def enable_printout_colors():
    """enables colored printouts for imsciutils printout messages"""
    ENABLE_COLOR = True

def printmsg(*messages):
    """prints a imsciutils message without any priority markers"""
    if ENABLE_COLOR:
        msg_str = ''.join([str(msg) for msg in messages])
        msg_str = colored(msg_str,
                            color=COLORS['printmsg'],
                            attrs=ATTRIBUTES['printmsg'])
        messages = [msg_str]

    print('(imsciutils) ', *messages)


def debug(*messages):
    """prints a imsciutils debug message"""
    if ENABLE_COLOR:
        msg_str = ''.join([str(msg) for msg in messages])
        msg_str = colored(msg_str,
                            color=COLORS['debug'],
                            attrs=ATTRIBUTES['debug'])
        messages = [msg_str]

    print('(imsciutils)[  DEBUG   ] ', *messages)


def info(*messages):
    """prints a imsciutils info message"""
    if ENABLE_COLOR:
        msg_str = ''.join([str(msg) for msg in messages])
        msg_str = colored(msg_str,
                            color=COLORS['info'],
                            attrs=ATTRIBUTES['info'])
        messages = [msg_str]

    print('(imsciutils)[   INFO   ] ', *messages)


def warning(*messages):
    """prints a imsciutils warning message"""
    if ENABLE_COLOR:
        msg_str = ''.join([str(msg) for msg in messages])
        msg_str = colored(msg_str,
                            color=COLORS['warning'],
                            attrs=ATTRIBUTES['warning'])
        messages = [msg_str]

    print('(imsciutils)[ WARNING  ] ', *messages)


def error(*messages):
    """prints a imsciutils error message"""
    if ENABLE_COLOR:
        msg_str = ''.join([str(msg) for msg in messages])
        msg_str = colored(msg_str,
                            color=COLORS['error'],
                            attrs=ATTRIBUTES['error'])
        messages = [msg_str]

    print('(imsciutils)[  ERROR   ] ', *messages)


def critical(*messages):
    """prints a imsciutils warning message"""
    if ENABLE_COLOR:
        msg_str = ''.join([str(msg) for msg in messages])
        msg_str = colored(msg_str,
                            color=COLORS['critical'],
                            attrs=ATTRIBUTES['critical'])
        messages = [msg_str]

    print('(imsciutils)[ CRITICAL ] ', *messages)
