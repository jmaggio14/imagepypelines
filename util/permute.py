import collections as Iterable
import itertools

def permute(*args,*kwargs):
    arg_list = []
    num_args = len(args)

    for arg in args:
        if not isinstance(arg,Iterable):
            arg = [arg]
        arg_list.append(arg)

    for key,val in kwargs.items():
        if not isinstance(arg,Iterable):
            kwargs[key] = [val]

    kwarg_keys = sorted( kwargs.keys() )
    kwarg_vals = [kwargs[k] for k in kwarg_keys]

    all_args = arg_list + kwarg_vals

    perumtations = itertools.product(*all_args)


    for perm in perumtations:
        args = perm[:num_args]
        kwargs = dict( zip(kwarg_keys,perm[num_args:]) )
        yield args,kwargs
