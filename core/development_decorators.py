import imsciutils as iu
import six
from termcolor import colored
import inspect
import collections

def depreciated(depreciation_msg):
    """
    Decorator for functions that are depreciated but still extant,

    Input:
        depreciation_msg (str,None): msg to print to the terminal when this function runs

    Example:
        @iu.depreciated("custom depreciation message here")
        def new_feature():
            do_something()

    """
    def _depreciated(func):
        def __depreciated(*args,**kwargs):
            iu.warning("DEPRECIATION WARNING:", depreciation_msg)
            return func(*args,**kwargs)

        return __depreciated
    return _depreciated



def experimental(experimental_msg=None):
    """
    Decorator for functions that are considered experimental,

    Input:
        experimental_msg (str,None): msg to print to the terminal when this function runs

    Example:
        @iu.experimental()
        def new_feature():
            do_something()

    """
    create_message = False
    if experimental_msg is None:
        create_message = True

    def _experimental(func):
        def __experimental(*args,**kwargs):
            if create_message:
                experimental_msg = "'{}' is an experimental feature. Its functionality may be buggy or exhibit undefined behavior!".format(func.__name__)
            iu.warning("EXPERIMENTAL WARNING:", experimental_msg)
            return func(*args,**kwargs)

        return __experimental
    return _experimental



def human_test(func):
    """
    Decorator for unit tests which require human interaction to verify their success,
    such as tests that perform complicated segmentation, classification, graphing
    or interaction with displays

    Example:
        iu.human_test # no parantheses are needed!
        def function_that_displays_something():
            do_something()

    """
    def _ask_input():
        if six.PY2:
            input = raw_input

        out = input("did the test for '{}' succeed? {Y}es? {N}o".format(func.__name__,
                                                                        Y=colored('Y',attrs=['bold']),
                                                                        N=colored('N',attrs=['bold'])))
        if out.lower() in ['yes','y']:
            return True
        elif out.lower() in ['no','n']:
            return False
        else:
            return _ask_input()

    def _human_test(*args,**kwargs):
        ret = func(*args,**kwargs)
        if _ask_input():
            return True
        else:
            return False

    return _human_test


def print_args(func):
    def _print_args(*args,**kwargs):
        """
        prints the arguments passed into the target
        """
        POSITIONAL    = '(  positional  )'
        KEYWORD       = '(   keyword    )'
        VARPOSITIONAL = '(var-positional)'
        VARKEYWORD    = '( var-keyword  )'

        arg_dict = collections.OrderedDict()
        vtypes = {}
        def __add_to_arg_dict(key,val,vtype):
            if iu.util.is_numpy_array(val):
                val = str( iu.Summarizer(val) )
            arg_dict[key] = val
            vtypes[key] = vtype


        spec = inspect.getfullargspec(func)
        specdefaults = [] if spec.defaults is None else spec.defaults
        specargs = [] if spec.args is None else spec.args
        speckwonlyargs = [] if spec.kwonlyargs is None else spec.kwonlyargs
        speckwonlydefaults = {} if spec.kwonlydefaults is None else spec.kwonlydefaults

        num_positional_passed_in = len(args)
        num_required = len(specargs) - len(specdefaults)

        # adding default positional args values to the dictionary
        for i,var_name in enumerate(specargs):
            if i < num_required:
                var = iu.util.red("No argument was passed in!",bold=True)
            else:
                var = specdefaults[i - num_required]

            vtype = POSITIONAL
            __add_to_arg_dict(var_name,var,vtype)

        # positional arguments passed in and varargs passed in
        for i in range(num_positional_passed_in):
            if i < num_required:
                var_name = specargs[i]
                vtype = POSITIONAL
            else:
                var_name = 'arg{}'.format(i)
                vtype = VARPOSITIONAL
            var = args[i]
            __add_to_arg_dict(var_name,var,vtype)

        # adding keyword only args to the dict
        for var_name in speckwonlyargs:
            var = iu.util.red("No argument was passed in!",bold=True)
            vtype = KEYWORD
            __add_to_arg_dict(var_name,var,vtype)
        for var_name,var in speckwonlydefaults.items():
            vtype = KEYWORD
            __add_to_arg_dict(var_name,var,vtype)

        # keyword arguments passed in
        for var_name in kwargs:
            if var_name in specargs:
                vtype = KEYWORD
            else:
                vtype = VARKEYWORD
            var = kwargs[var_name]
            __add_to_arg_dict(var_name,var,vtype)

        # formatting the actual string to be printed out
        iu.info("running '{}' with the following args:\n".format(func.__name__))
        longest_arg_name = max(len(k) for k in arg_dict)
        arg_string = ""
        arg_string += "\t{buf1}type{buf1}|{buf2} arg_name {buf2}|  value\n".format(
                                                            buf1=' ' * (len(POSITIONAL) // 2 - 4),
                                                            buf2=' ' * (longest_arg_name // 2 - 7),)
        arg_string += '\t' + '='*50 + '\n'
        arg_string += ''.join(["\t{} {} : {}\n".format(vtypes[k], k+(' ' * (longest_arg_name-len(k))), v) for k,v in arg_dict.items()])
        print( arg_string )

        ret = func(*args,**kwargs)
        return ret
    return _print_args
