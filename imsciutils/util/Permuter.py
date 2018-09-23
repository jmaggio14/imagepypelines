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
