"""
This file provides functions which will be used in the imgscitools
backend to print out messages
"""


def printmsg(*messages):
    """prints a imgscitools message without any priority markers"""
    print('(imgscitools) ', *messages)


def debug(*messages):
    """prints a imgscitools debug message"""
    print('(imgscitools)[  DEBUG   ] ', *messages)


def info(*messages):
    """prints a imgscitools info message"""
    print('(imgscitools)[   INFO   ] ', *messages)


def warning(*messages):
    """prints a imgscitools warning message"""
    print('(imgscitools)[ WARNING  ] ', *messages


def error(*messages):
    """prints a imgscitools error message"""
    print('(imgscitools)[  ERROR   ] ', *messages


def critical(*messages):
    """prints a imgscitools warning message"""
    print('(imgscitools)[ CRITICAL ] ', *messages
