"""
Add additional tasks to your pipelines
======================================


"""
import numpy as np
import imagepypelines as ip


###############################################################################
@ip.blockify()
def add1(a, b):
    return a+1, b+1

@ip.blockify()
def subtract1(a, b):
    return a-1, b-1

@ip.blockify()
def average(x1, x2):
    return (x1 + x2) / 2

###############################################################################
# Our Example Pipeline
# --------------------
# don't pay too much attention to this, we're just creating a random meaningless
# pipeline

pipeline = ip.Pipeline({
                        'a': ip.Input(0),
                        'b': ip.Input(1),
                        ('a_plus_1','b_plus_1') : (add1, 'a', 'b'),
                        ('a_minus_1','b_minus_1') : (subtract1, 'a', 'b'),
                        }
                        )

###############################################################################
# Just call the pipeline's `update` function
# ------------------------------------------

more_tasks = {
            'average_a': (average,'a_plus_1','a_minus_1'),
            'average_b': (average,'b_plus_1','b_minus_1'),
             }

pipeline.update(more_tasks)

###############################################################################
# Let's process some data!
# ------------------------
# Let's create the inputs
a = [10]
b = [-10]

# Number and view the images!
processed = pipeline.process(a,b)

assert processed['average_a'][0] == a[0]
assert processed['average_b'][0] == b[0]
