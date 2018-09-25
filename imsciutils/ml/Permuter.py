#
# @Email:  jmaggio14@gmail.com
#
# MIT License
#
# Copyright (c) 2018 Jeff Maggio, Nathan Dileas, Ryan Hartzell
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
from collections import Iterable
import itertools
import numpy as np

from .ConfigFactory import ConfigFactory
from .. import core

@core.deprecated("'Permuter' has been renamed to 'ConfigFactory', references to\
    'Permuter' will be removed in a future version")
class Permuter(ConfigFactory):
    pass

def main():
    arg_trials = [
            [1,2,3],
            ['a','b','c'],
            ['y','z'],
            ]

    kwarg_trials = {
                'first':None,
                'second':['I','J','K'],
                'third':['i','j','k'],
                }

    perm_gen = Permuter(*arg_trials,**kwarg_trials)

    perm_idx = 0
    for args,kwargs in perm_gen:
        print( args,kwargs )
        print( perm_gen.remaining(),'permutation remaining' )
        perm_idx += 1

    print( perm_idx )
    print( len(perm_gen) )

if __name__ == "__main__":
    main()
