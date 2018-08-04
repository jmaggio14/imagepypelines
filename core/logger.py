"""
This file provides functions which will be used in the imscitools
backend to print out messages
"""


def printmsg(*messages):
    """prints a imscitools message without any priority markers"""
    print('(imscitools) ', *messages)


def debug(*messages):
    """prints a imscitools debug message"""
    print('(imscitools)[  DEBUG   ] ', *messages)


def info(*messages):
    """prints a imscitools info message"""
    print('(imscitools)[   INFO   ] ', *messages)


def warning(*messages):
    """prints a imscitools warning message"""
    print('(imscitools)[ WARNING  ] ', *messages


def error(*messages):
    """prints a imscitools error message"""
    print('(imscitools)[  ERROR   ] ', *messages


def critical(*messages):
    """prints a imscitools warning message"""
    print('(imscitools)[ CRITICAL ] ', *messages
