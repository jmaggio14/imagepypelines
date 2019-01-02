
from .. import Pipeline
from .. import builtin_blocks as blocks

def LinearTransform(m,b):
    mult = blocks.Multiply(m)
    add = blocks.Add(b)

    pipeline = Pipeline([mult,add],name="LinearTransform")
    return pipeline
