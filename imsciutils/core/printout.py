import os
import imsciutils as iu

def get_default_printer():
    """gets the imsciutils default printer"""
    return iu.get_printer('imsciutils')

def debug(*messages):
    """prints a 'debug' level message to the imsciutils default printer"""
    printer = get_default_printer()
    printer.debug(*messages)

def info(*messages):
    """prints a 'info' level message to the imsciutils default printer"""
    printer = get_default_printer()
    printer.info(*messages)

def warning(*messages):
    """prints a 'warning' level message to the imsciutils default printer"""
    printer = get_default_printer()
    printer.warning(*messages)

def error(*messages):
    """prints a 'error' level message to the imsciutils default printer"""
    printer = get_default_printer()
    printer.error(*messages)

def critical(*messages):
    """prints a 'critical' level message to the imsciutils default printer"""
    printer = get_default_printer()
    printer.critical(*messages)

def comment(*messages):
    """prints a 'comment' level message to the imsciutils default printer"""
    printer = get_default_printer()
    printer.comment(*messages)
