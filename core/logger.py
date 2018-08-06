"""
This file provides functions which will be used in the imsciutils
backend to print out messages
"""


def printmsg(*messages):
    """prints a imsciutils message without any priority markers"""
    print('(imsciutils) ', *messages)


def debug(*messages):
    """prints a imsciutils debug message"""
    print('(imsciutils)[  DEBUG   ] ', *messages)


def info(*messages):
    """prints a imsciutils info message"""
    print('(imsciutils)[   INFO   ] ', *messages)


def warning(*messages):
    """prints a imsciutils warning message"""
    print('(imsciutils)[ WARNING  ] ', *messages)


def error(*messages):
    """prints a imsciutils error message"""
    print('(imsciutils)[  ERROR   ] ', *messages)


def critical(*messages):
    """prints a imsciutils warning message"""
    print('(imsciutils)[ CRITICAL ] ', *messages)
