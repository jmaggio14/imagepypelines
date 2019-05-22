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
    ArrayIn(['N','M']) : ArrayType(['N*M','1'])

2) be able to apply a rule to an unknown number of axis
    ArrayOut(all_axis_rule="5*N")

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
import copy
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


INPUT_CHARS_ALLOWED = list(string.ascii_letters + '_0123456789')

def varname_check(var):
    if not all( (v in INPUT_CHARS_ALLOWED) for v in tuple(var) ):
        raise ValueError("variable names can only be ascii letters, numbers"
            + " or '_'. '%s' contains banned chars" % var)


################################################################################
#                            Builtin IO Types
################################################################################
class AnyType:
    pass


class ArrayIn(object):
    def __init__(self, axes="arbitrary"):

        if axes == "arbitrary":
            # the input array could be any shape, thus we can't define the names
            self.axes = "arbitrary"
            self.varnames = None
            self.naxes = None

        else:
            self.axes = []
            self.varnames = []
            for i,var in enumerate(axes):
                # if the axis is an integer, we have to create our own varnames
                if isinstance(var, (float,int) ):
                    self.axes.append( int(var) )
                    self.varnames.append('$' + str(i))

                else:
                    varname_check(var)

                    if var[0].isdigit():
                        raise ValueError("variable names cannot begin with a number")

                    self.axes.append(var)
                    self.varnames.append(var)

            self.naxes = len(self.axes)


    def __iter__(self):
        for ax in self.axes:
            yield ax

    def __str__(self):
        return "ArrayIn%s" % self.axes

    def __repr__(self):
        return str(self)


class GenericIn(object):
    def __init__(self, val, varname='X'):
        varname_check(varname)
        self.val = val
        self.varname = varname

    def __str__(self):
        return self.__class__.__name__ + ('(%s)' % str(self.val))

    def __repr__(self):
        return str(self)

class ConstantIn(GenericIn):
    pass

class IntIn(GenericIn):
    pass

class FloatIn(GenericIn):
    pass




class ArrayOut(object):
    def __init__(self,
                rules="arbitrary",
                all_axis_rule=None):

        self.rules = rules
        self.all_axis_rule = all_axis_rule
        self.shape = None

    def init(self, varnames):

        ### ERROR CHECK ###
        if self.all_axis_rule:
            self.shape = []
            self.rules = [self.all_axis_rule] * len(varnames)

        if isinstance(self.rules, str):
            ok = ("arbitrary", "input_shape")
            assert shape in ok, "shape must axial expressions or one of %s" % ok
            self.shape = []

        else:
            # go through each element in the shape and evaluate it as a
            # string or 'constant' type
            self.shape = []
            for axis in self.rules:
                # keep numbers the same, but as AxisExpressions
                if isinstance(axis,(float,int)):
                    self.shape.append( AxisInteger(axis) )

                # turn strings into Expressions
                elif isinstance(axis, str):
                    self.shape.append( AxisExpression(axis, varnames) )

                else:
                    raise ValueError(
                        "Array Axes can only be defined as strings or numbers")

    def output(self, array_in):
        if self.shape == "arbitrary":
            return ArrayIn("arbitrary")

        elif self.shape == "input_shape":
            return array_in

        else:
            return ArrayIn( [ax.evaluate(array_in.axes) for ax in self.shape] )


    def __str__(self):
        # if self.all_axis_rule:
        #     return 'ArrayOut[ {} for all axes ]'.format(self.all_axis_rule)
        return 'ArrayOut[' + ', '.join( repr(ax) for ax in self.shape ) + ']'

    def __repr__(self):
        return str(self)









################################################################################
#                          Axis Length Evaluation
################################################################################
class AxisKernel(ABC):
    @abstractmethod
    def evaluate(self, axes_vals):
        pass

class AxisInteger(AxisKernel):
    def __init__(self, val):
        self.val = int( val )

    def evaluate(self, axes_vals=None):
        return self.val

    def __get__(self):
        return self.val

    def __str__(self):
        return str(self.val)

    def __repr__(self):
        return str(self)


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


    def evaluate(self, axes_vals):
        # NOTE: eval must not have access to module locals and globals
        # the only thing it should have access to the values in FUNCTIONS
        # FUNCTIONS is copied as part of sanitation precaution
        namespace = copy.deepcopy(FUNCTIONS)
        if self.num_vars > 0:
            out = eval(self.sanitized.format(*axes_vals), {}, namespace)
        else:
            out = eval(self.sanitized, {}, namespace)
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
            # Special Case for Array Inputs and Outputs
            if isinstance(io[1], ArrayOut) and isinstance(io[0], ArrayIn):
                io[1].init( io[0].varnames )


            self.inputs.append(io[0])
            self.outputs.append(io[1])

            if len(io) == 2:
                self.descriptions.append("No description provided")
            else:
                assert isinstance(io[2], str), "description must be string"
                self.descriptions.append(io[2])

    def output(self, input_):
        if isinstance(input_, ArrayIn):
            out = self._array_in(input_)

        else:
            raise RuntimeError("non array inputs not yet supported")

        if len(out) == 0:
            raise IncompatibleTypes("invalid input type, must be"\
                 + "({}) not {}".format(self.inputs, input_))

        return out



    def _array_in(self, arr_in):
        out = set()

        for ok_array_in, corresponding_out in zip(self.inputs, self.outputs):
            # skip this iteration if ok_input isn't an array
            if not isinstance(ok_array_in, ArrayIn):
                continue

            if ok_array_in.axes == 'arbitrary':
                # this io map input can accept any shaped ArrayIn
                out.add( arr_in )

            elif len(ok_array_in.axes) == len(arr_in.axes):
                out.add( corresponding_out.output(arr_in) )

        return out

    def __str__(self):
        io_strs = []
        for i,o,d in zip(self.inputs,self.outputs,self.descriptions):
            io_strs.append( '{} --> {}'.format(i,o) )
            if not d is None:
                io_strs[-1] += "   ( %s )" % d

        return '\n'.join(io_strs)

    def __repr__(self):
        return str(self)








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





    # testing IoMap
    import numpy as np
    test_arr1 = np.random.rand(512,512,3)
    test_arr2 = np.random.rand(512,512)
    io_kernel = [
                [ArrayIn(['N','M',3]),
                    ArrayOut(['N','M']),
                    "convert RGB input to Grayscale"],
                [ArrayIn(['N','M']),
                    ArrayOut(['N','M']),
                    "perform no operation on Grayscale images "],
                [ArrayIn(['N','M']),
                    ArrayOut(['2*N','3*M']),
                    "upsample random Grayscale images "],
                [ArrayIn(['A','D','P']),
                    ArrayOut(all_axis_rule="10*A"),
                    "this is a test so I'm not going to bother with a description"],
                ]

    io_map = IoMap(io_kernel)
    output1 = io_map.output( ArrayIn(test_arr1.shape) )
    output2 = io_map.output( ArrayIn(test_arr2.shape) )
    import pdb; pdb.set_trace()







#END
