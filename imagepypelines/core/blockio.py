# # @Email: jmaggio14@gmail.com
# # @Website: https://www.imagepypelines.org/
# # @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# # @github: https://github.com/jmaggio14/imagepypelines
# #
# # Copyright (c) 2018-2019 Jeff Maggio, Nathan Dileas, Ryan Hartzell
# #
# """
#
# goal is to enable this functionality
#
# 1) specify an axis length by equation
#     ArrayType(['N','M']) : ArrayType(['N*M','1'])
#
# 2) be able to apply a rule to an unknown number of axis
#     ArrayType(all_axis="5*N")
#
# 3) be able to pass in your own function to generate an output
#     FuncType(func) where func takes in input_type
#
# 4) add dimensional flexability
#     ArrayType(['<expr>'], error='+/-1')
#
# 5)
#
# TODO:
#     [ ] string compiler
#     [ ] new IoMap structure
#
# """
#
# import math
# import string
# from abc import ABC
#
#
# # ============================ Globals ============================
# OPERATORS = ['+','-','*','**','/','%']
# """acceptable operators"""
#
# CHOP_CHARS = OPERATORS + ['(',')']
# """chracters used to split the expression string"""
#
# FUNCTIONS = {
#             # python builtin math functions
#             'abs':abs,
#             'max':max,
#             'min':min,
#             'pow':pow,
#             'round':round,
#             # python math module functions
#             'ceil':math.ceil,
#             'copysign':math.copysign,
#             'factorial':math.factorial,
#             'floor':math.floor,
#             'fmod':math.fmod,
#             'gcd':math.gcd,
#             'trunc':math.trunc,
#             'exp':math.exp,
#             'expm1':math.expm1,
#             'log':math.log,
#             'log1p':math.log1p,
#             'log1p':math.log1p,
#             'log10':math.log10,
#             'pow':math.pow,
#             'sqrt':math.sqrt,
#             'acos':math.acos,
#             'asin':math.asin,
#             'atan':math.atan,
#             'atan2':math.atan2,
#             'cos':math.cos,
#             'sin':math.sin,
#             'tan':math.tan,
#             'hypot':math.hypot,
#             'degrees':math.degrees,
#             'radians':math.radians,
#             'acosh':math.acosh,
#             'asinh':math.asinh,
#             'atanh':math.atanh,
#             'cosh':math.cosh,
#             'sinh':math.sinh,
#             'tanh':math.tanh,
#             'erf':math.erf,
#             'erfc':math.erfc,
#             'gamma':math.gamma,
#             'lgamma':math.lgamma,
#             # Constants
#             'pi':math.pi,
#             'e':math.e,
#             }
# """dictionary of acceptable functions and constants in axis expressions"""
#
# ALLOWED = CHOP_CHARS + list(FUNCTIONS.keys())
#
#
# INPUT_CHARS_ALLOWED = list(string.ascii_letters + '_')
# # ============================ Base Class(es) ============================
# class Output(ABC):
#     @abstractmethod
#     def output(self,input_type):
#         pass
#
#
# class AxisKernel(ABC):
#     @abstractmethod
#     def evaluate(self):
#         pass
#
#     @abstractmethod
#     def __get__(self):
#         pass
#
# # ======================== Builtin IO Types ========================
# class ArrayType(object):
#     def __init__(self,shape):
#         # go through each element in the shape and evaluate it as a
#         # string or 'constant' type
#         self.shape = []
#         for axis in out_shape:
#             # keep numbers the same
#             if isinstance(axis,(float,int)):
#                 self.shape.append( int(axis) )
#
#             # turn some strings into
#             elif isinstance(axis,str):
#                 self.shape.append( AxisExpression(axis) )
#
#             else:
#                 raise ValueError(
#                     "Array Axes can only be defined as strings or numbers")
#
#
# # ======================== Builtin IO Output Classes ========================
# class ConstantOutput(Output):
#     def output(self,input_type):
#         return input_type
#
# class ArrayOutput(Output):
#     def __init__(self,
#                 input_shape,
#                  output_shape
#                  ):
#
#         # generate axis variable names for each axis in the input shape
#         # inputs must be strings or integers
#         varnames = []
#         for i,axis in enumerate(input_shape):
#             # if our axis is an integer, we can just generate a variable name
#             # e.g. [10,20,'C'] --{make varnames}--> ['$AXIS1','$AXIS2','C']
#             if isinstance(axis,int):
#                 varnames.append('$AXIS%s' % i)
#
#             # raise a ValueError if the input axis contains a banned character
#             elif isinstance(axis,str):
#                 if not all(chr in INPUT_CHARS_ALLOWED for chr in axis):
#                     raise ValueError(
#                         "input axis can only contain {}"\
#                         .format(INPUT_CHARS_ALLOWED))
#                 varnames.append(axis)
#
#             # if it's not a integer or string, then we have to raise a
#             # ValueError
#             else:
#                 raise ValueError("only acceptable input types are int and str")
#
#
#         self.axis_kernels = ArrayType(output_shape)
#
#     def output(self, input_array):
#         axes = input_array.shape
#         out_shape = [ker.evaluate(axes,self.varnames) for ker in self.axis_kernels]
#         return ArrayType(out_shape)
#
#
# # ========================= Axis Length Evaluation =========================
# class AxisInteger(AxisKernel):
#     def __init__(self,val):
#         self.val = val
#
#     def evaluate(self,varnames=None):
#         return self.val
#
#     def __get__(self):
#         return self.val
#
#
# class AxisExpression(AxisKernel):
#     def __init__(self,expr,varnames):
#         # break string up into pieces for sanitization
#         chopped = []
#         start = 0
#         current = 0
#         for chr in expression:
#             if (chr in OPERATORS) or (current == len(expression)):
#                 chopped.append(expression[start:current])
#                 chopped.append(chr)
#                 start = current
#             else:
#                 current += 1
#
#         # sanitize the input
#         for i,chop in enumerate(chopped):
#             if chop in varnames:
#                 # replace varname with a string insertion so it can be filled
#                 # in later on
#                 # (N*M) --> ({0}*{1})
#                 chopped[i] = '{%s}' % str( varnames.index(chop) )
#
#             elif chop not in ALLOWED:
#                 # reject anything that's not in our criteria
#                 raise ValueError(
#                     "invalid variable, operator or function {}".format(chop))
#
#         self.sanitized = ''.join(chopped)
#
#
#     def evaluate(self,axes):
#         # NOTE: eval must not have access to module locals and globals
#         # the only thing it should have access to the values in FUNCTIONS
#         out = eval(self.sanitized.format(*axes), {}, FUNCTIONS)
#         return int( out )
#
#
# # ============================== IoMap ==============================
#
# class IoMap(object):
#     def __init__(self,io_map_dict):
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
# #END
