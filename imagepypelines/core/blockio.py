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


# ============================ Globals ============================
OPERATORS = '+-*/%^'

FUNCTIONS = {
            # python builtins
            'abs':abs,
            'max':max,
            'min':min,
            'pow':pow,
            'round':round,
            # python math module
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
            'pow':math.pow,
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
            }
"""dictionary of acceptable functions for use in axis expressions"""

RESERVED = {'pi':math.pi,
            'e':math.e}
"""Dictionary of reserved constant values such as e and pi"""

# ============================ String Parsing ============================
class Expression(object):
    def __init__(self,expr):
        """
        1) check syntax
        2) split string by operators
        3) find builtin functions
        4) identify variables
        5) compile
        """



# ============================ Builtin IO Types ============================
class FuncType(object):
    def __init__(self,func):
        assert callable(func),"FuncType must be instantiated with a function"
        self.func = func

    def __call__(self,input_type):
        return self.func(input_type)


class ArrayType(FuncType):
    def __init__(self,
                 shape,
                 all_axis_rule=None,
                 error=None):

        # if there is a rule that applies to all axes, ignore the shape and build
        # build a ru
        if all_axis_rule:
            self.shape = None
            # TODO: generate string parse here

        else:
            expressions = [ Expression(expr) for expr in self.shape ]

        self.shape = shape
        all_axis_rule = None















#END
