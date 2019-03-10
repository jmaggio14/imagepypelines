# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018 Jeff Maggio, Nathan Dileas, Ryan Hartzell
#
import string
from math import *
import sys

CURR_MOD = sys.modules[__name__]

OPERATORS = '+-*/%^'
INPUT_ALLOWED = string.ascii_letters + '_'
OUTPUT_ALLOWED = INPUT_ALLOWED + OPERATORS + VAR + '()'
CHOP_CHARS = OPERATORS + '()'

FUNCTIONS = [
            # python builtins
            'abs',
            'max',
            'min',
            'pow',
            'round',
            # python math module
            'ceil',
            'copysign',
            'factorial',
            'floor',
            'fmod',
            'gcd',
            'trunc',
            'exp',
            'expm1',
            'log',
            'log1p',
            'log1p',
            'log10',
            'pow',
            'sqrt',
            'acos',
            'asin',
            'atan',
            'atan2',
            'cos',
            'sin',
            'tan',
            'hypot',
            'degrees',
            'radians',
            'acosh',
            'asinh',
            'atanh',
            'cosh',
            'sinh',
            'tanh',
            'erf',
            'erfc',
            'gamma',
            'lgamma',
            ]
RESERVED = ['pi','e']

class CompiledOutput(object):
    def __init__(self,input_vars,expression):
        # perform check and reject
        # input
        if not all(chr in INPUT_ALLOWED for chr in input_vars):
            raise ValueError("input axis can only contain {}".format(INPUT_ALLOWED))
        # expression
        if not all(chr in OUTPUT_ALLOWED for chr in expression):
            raise ValueError("expression can only contain {}".format(OUTPUT_ALLOWED))

        self.input_vars = input_vars
        self.expression = expression
        self.sections = []

        # break string up into pieces for compilations
        chopped = []
        start = 0
        current = 0
        for chr in expression:
            if (chr in CHOP_CHARS) or (current == len(expression)):
                chopped.append(expression[start:current])
                chopped.append(chr)
                start = current
            else:
                current += 1

        # iterate through chopped pieces and process
        for i in range(len(chopped)):
            chop = chopped[i]

            # TODO, add function support
            # # check if chop is a function
            # if chop in FUNCTIONS:
            #     self.sections.append( getattr(CURR_MOD,chop) )

            # check if chop is an operator
            if chop in operators:
                # check to make sure the previous chop wasn't an operator
                if len(self.sections) == 0:
                    pass
                elif self.sections[-1] in OPERATORS:
                    raise ValueError("cannot have two operators next to each other")
                # otherwise append an operator object
                self.sections.append(chop)

            # check if chop is a variable
            elif chop in self.input_vars:
                # replace with an axis definition $1 --> axis1, $2 --> axis2
                chop.append('$' + str( self.input_vars.index(chop) ) )

            # otherwise it's an unrecognized symbol
            else:
                raise ValueError("unrecognized operator or variable {}".format(chop))


    def __call__(self,*axis_values):
        for s in self.sections:



#
# # DEBUG
# INPUT = ['N','M','O']
# OUTPUT = ["N*M","10+(N*5)"]
# # END DEBUG
#
# def check_input():
#
# def compile(input_varss, axis_string):
#     # perform check and rejections
#     if not all(chr in ALLOWED for chr in group_str):
#         raise ValueError("expression can only contain {}".format(ALLOWED))
#
#
#




# class Group(object):
#     def __init__(self,group_str):
#         self.group_str = group_str
#         self.__sanitize(group_str)
#
#         # check if all characters in the group are acceptable
#         if not all(chr in ALLOWED for chr in group_str):
#             raise ValueError("expression can only contain {}".format(ALLOWED))
#
#     def __compile(self):
#         # divide the string by the operators
#         sections = re.split("[{}]".format(OPERATORS+PARENTHESES), self.group_str)
#
#         # check to make sure there is an even number of openning and closing parantheses
#
#
#
# def find_char(chr,s):
#     """Gets the indices of all instances of a character in a string
#     Args:
#         s (str): string to search
#         chr (str): char to search for in the string
#
#     Returns:
#         list: indices of char appearances in the strings
#     """
#     return [i for i, ltr in enumerate(s) if ltr == ch]
#
# def find_groups(expression):
#     """
#     find groups of substring located between an open and close parantheses
#
#     Args:
#         expression (str):
#     """
#     open_indices = find_char('(', expression)
#     close_indices = find_char(')', expression)
#
#     # check to make sure there is a corresponding closing paranthesis for every open one
#     if len(open_indices) > len(close_indices):
#         raise ValueError("there must be corresponding closing paranthesis for every openning one")
#     elif len(close_indices) > len(open_indices):
#         raise ValueError("there must be corresponding openning paranthesis for every closing one")
#
#     for open,close in open_indices,close_indices[::-1]:
