# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018-2019 Jeff Maggio, Nathan Dileas, Ryan Hartzell
#
"""

goal is to enable this functionality

1) specify an axis length by equation
    ArrayType(['N','M']) : ArrayType(['N*M','1'])

2) be able to apply a rule to an unknown number of axis
    ArrayType(all_axis="5*N")

3) be able to pass in your own function to generate an output
    FuncType(func) where func takes in input_type

4) add dimensional flexability
    ArrayType(['<expr>'], error='+/-1')

5)

TODO:
    [ ] string compiler
    [ ] new IoMap structure

"""

import math
import string
from abc import ABC, abstractmethod


# ============================ Globals ============================
OPERATORS = sorted(['**','==','>=','<=','!=','+','-','*','/','%'], key=len, reverse=True)
"""acceptable operators, sorted by descending length"""

CHOP_CHARS = OPERATORS + ['(',')',',',' ']
"""characters used to split the expression string"""

FUNCTIONS = {
            # python builtin math functions
            'abs':abs,
            'max':max,
            'min':min,
            'pow':pow,
            'round':round,
            # python math module functions
            'ceil':math.ceil,
            'copysign':math.copysign,
            'factorial':math.factorial,
            'floor':math.floor,
            'fmod':math.fmod,
            'gcd':math.gcd,
            'trunc':math.trunc,
            'exp':math.exp,
            'expm1':math.expm1,
            'log':math.log,
            'log1p':math.log1p,
            'log1p':math.log1p,
            'log10':math.log10,
            'sqrt':math.sqrt,
            'acos':math.acos,
            'asin':math.asin,
            'atan':math.atan,
            'atan2':math.atan2,
            'cos':math.cos,
            'sin':math.sin,
            'tan':math.tan,
            'hypot':math.hypot,
            'degrees':math.degrees,
            'radians':math.radians,
            'acosh':math.acosh,
            'asinh':math.asinh,
            'atanh':math.atanh,
            'cosh':math.cosh,
            'sinh':math.sinh,
            'tanh':math.tanh,
            'erf':math.erf,
            'erfc':math.erfc,
            'gamma':math.gamma,
            'lgamma':math.lgamma,
            # Constants
            'pi':math.pi,
            'e':math.e,
            '':'',
            }
"""dictionary of acceptable functions and constants in axis expressions"""

ALLOWED = CHOP_CHARS + list(FUNCTIONS.keys())


INPUT_CHARS_ALLOWED = list(string.ascii_letters + '_')
# ============================ Base Class(es) ============================
class Output(ABC):
    @abstractmethod
    def output(self,input_type):
        pass


class AxisKernel(ABC):
    @abstractmethod
    def evaluate(self):
        pass

# ======================== Builtin IO Types ========================
class ArrayIn(object):
    def __init__(self,shape):
        # go through each element in the shape and evaluate it as a
        # string or 'constant' type
        self.shape = []
        for axis in out_shape:
            # keep numbers the same, but as AxisExpressions
            if isinstance(axis,(float,int)):
                self.shape.append( AxisInteger(axis) )

            # turn strings into Expressions
            elif isinstance(axis, str):
                self.shape.append( AxisExpression(axis) )

            else:
                raise ValueError(
                    "Array Axes can only be defined as strings or numbers")


# ======================== Builtin IO Output Classes ========================
# class ConstantOutput(Output):
#     def output(self,input_type):
#         return input_type
#
# class ArrayOutput(Output):
#     def __init__(self, shape):
#
#         # generate axis variable names for each axis in the input shape
#         # inputs must be strings or integers
#         varnames = []
#         for i,axis in enumerate(shape):
#             # if our axis is an integer, we can just generate a variable name
#             # e.g. [10,20,'C'] --{make varnames}--> ['$AXIS1','$AXIS2','C']
#             if isinstance(axis, int):
#                 varnames.append('$AXIS%s' % i)
#
#             # raise a ValueError if the input axis contains a banned character
#             elif isinstance(axis, str):
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
#         return ArrayIn(out_shape)


# ========================= Axis Length Evaluation =========================
class AxisInteger(AxisKernel):
    def __init__(self, val):
        self.val = int( val )

    def evaluate(self,varnames=None):
        return self.val

    def __get__(self):
        return self.val


class AxisExpression(AxisKernel):
    def __init__(self,expr,varnames):
        # replace all whitespace with a single space char
        expr = ' '.join(expr.split())

        # break string up into pieces for sanitization
        chopped = []
        chop = ""
        idx = 0
        while idx < len(expr):
            for op in CHOP_CHARS:
                # import pdb; pdb.set_trace()
                if expr[idx:min(idx+len(op), len(expr))] == op:
                    chopped.append(chop)
                    chopped.append(op)
                    chop = ""
                    idx += (len(op))
                    break

            if idx < len(expr):
                chop += expr[idx]

            idx += 1

        if chop != "":
            chopped.append(chop)



        # sanitize the input
        for i,chop in enumerate(chopped):
            # check if chop is a numeric
            try:
                float(chop)
                continue
            except ValueError:
                pass

            if chop in varnames:
                # replace varname with a string insertion so it can be filled
                # in later on
                # (N*M) --> ({0}*{1})
                chopped[i] = '{%s}' % str( varnames.index(chop) )

            # same as the above statement, except with whitespace removed
            elif chop.replace(' ','') in varnames:
                chopped[i] = '{%s}' % str( varnames.index(chop.replace(' ','')) )


            elif chop.replace(' ','') not in ALLOWED:
                # reject anything that's not in our criteria
                raise ValueError(
                    "invalid variable, operator, or function {}".format(chop))

        self.sanitized = ''.join(chopped)
        self.varnames = varnames
        self.readable = self.sanitized.format(*self.varnames)
        self.num_vars = len(varnames)


    def evaluate(self,axes_vals):
        # NOTE: eval must not have access to module locals and globals
        # the only thing it should have access to the values in FUNCTIONS
        if self.num_vars > 0:
            out = eval(self.sanitized.format(*axes_vals), {}, FUNCTIONS)
        else:
            out = eval(self.sanitized, {}, FUNCTIONS)
        return int( out )

    def __str__(self):
        return self.readable

    def __repr__(self):
        return "Axis(" + self.readable + ")"



# ============================== IoMap ==============================

class IoMap(object):
    """

    IoMaps are now instantiated like this

    io_kernel = [
                [ArrayIn(['N','M']), ArrayOut(['N*M',1]), "optional description"],
                ]
    """
    def __init__(self, io_kernel):
        # check for the proper input
        assert isinstance(io_kernel,(list,tuple)),\
            "the io_kernel must a list of lists"
        assert all(isinstance(io,(list,tuple)) for io in io_kernel), \
            "the io_kernel must a list of lists"

        self.inputs = []
        self.outputs = []
        self.descriptions = []
        for io in io_kernel:
            self.inputs.append(io[0])
            self.outputs.append(io[1])

            if len(io) == 2:
                self.descriptions.append("No description provided")
            else:
                assert isinstance(io[2], str), "description must be string"
                self.descriptions.append(io[2])

    def output(self, input_):
        if isinstance(input_, ArrayIn):
            return self._array_in(input_)
        elif isinstance(input_, Constant)

    def _array_in(self, arr_in):
        pass

    def _constant_in(self, const_in):
        pass















if __name__ == "__main__":

    def eval_axis(axis, vals, real):
        evaled = axis.evaluate( vals )
        var_string = '   (' + ', '.join(['{}={}'.format(i,j) for i,j in zip(axis.varnames,vals)]) + ')' if len(vals) else ''

        if evaled == real:
            print("(correct) ", axis, "-->", evaled, var_string )
        else:
            print("(failed) ", axis, " evals to ", evaled, " should be", real, var_string  )


    a = AxisExpression("N*M", ['N','M'])
    b = AxisExpression("A**B", ['A','B'])
    c = AxisExpression("cos(pi)", [])
    d = AxisExpression("radians(360)", [])
    e = AxisExpression("ceil(9.9)", [])
    f = AxisExpression("max(.01, .001)", [])
    g = AxisExpression("sqrt(N) + pow(M,6)", ['N','M'])
    h = AxisExpression("10 >= N", ['N'])
    i = AxisExpression("A**2 + B**2 + C**2 + D**2 + E**2 + F**2" , ['A','B','C','D','E','F'])
    j = AxisExpression("N" , ['N'])

    eval_axis(a, [10,15], 150)
    eval_axis(b, [2,3], 8)
    eval_axis(c, [], -1)
    eval_axis(d, [], 6)
    eval_axis(e, [], 10)
    eval_axis(f, [], 0)
    eval_axis(g, [16,2], 4+2**6)
    eval_axis(h, [9], 1)
    eval_axis(i, list( range(1,7) ), 91)
    eval_axis(j, [1e3], 1e3)







#END
