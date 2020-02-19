# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018-2019 Jeff Maggio, Nathan Dileas, Ryan Hartzell
from ..Logger import get_logger
from .constants import CV2_INTERPOLATION_TYPES
from .constants import NUMPY_TYPES
from .Exceptions import InvalidInterpolationType
from .Exceptions import InvalidNumpyType
import inspect
import collections
import time
from termcolor import colored
import numpy as np

TIMER_LOGGER = get_logger('TIMER')

################################################################################
#                                 Error Checking
################################################################################
"""
Helper functions that contain canned tests or checks that we will run
frequently
"""
def interpolation_type_check(interp):
    """
    checks to see if the interpolation type is one of the acceptable
    values specified in opencv, otherwise raises an
    imagepypelines.InvalidInterpolationType error
    """
    if interp not in CV2_INTERPOLATION_TYPES:
        raise InvalidInterpolationType(interp)

    return True


def dtype_type_check(dtype):
    """
    checks to see if the interpolation type is one of the acceptable
    values specified in opencv, otherwise raises an
    imagepypelines.InvalidInterpolationType error
    """
    if dtype not in NUMPY_TYPES:
        raise InvalidNumpyType(dtype)

    return True


################################################################################
#                                 Decorators
################################################################################

def print_args(func):
    """Decorator to print out the arguments that a function is running with,
    this includes: arguments passed in, default values that are unspecified,
    varargs ``(*args)``, and varkwargs ``(**kwargs)``

    Args:
        func (callable): function or callable to print input arguments of
    """
    def _print_args(*args,**kwargs):
        """
        prints the arguments passed into the target
        """
        POSITIONAL    = 'positional    |'
        KEYWORD       = 'keyword       |'
        VARPOSITIONAL = 'var-positional|'
        VARKEYWORD    = 'var-keyword   |'
        DEFAULT       = 'default       |'
        PRINTER = get_logger(func.__name__)

        arg_dict = collections.OrderedDict()
        vtypes = {}
        def __add_to_arg_dict(key,val,vtype):
            if isinstance(val, np.ndarray):
                val = str( Summarizer(val) )
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
                var = colored("No argument was passed in!",attrs=['bold'])
            else:
                var = specdefaults[i - num_required]

            vtype = DEFAULT
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
            var = color.red("No argument was passed in!",bold=True)
            vtype = KEYWORD
            __add_to_arg_dict(var_name,var,vtype)
        for var_name,var in speckwonlydefaults.items():
            vtype = DEFAULT
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
        PRINTER.info("running '{}' with the following args:".format(func.__name__))
        if len(arg_dict) == 0:
            __add_to_arg_dict('None','','')
        longest_arg_name = max(len(k) for k in arg_dict)
        arg_string = ''.join(["\t{} {} : {}\n".format(vtypes[k], k+(' ' * (longest_arg_name-len(k))), v) for k,v in arg_dict.items()])
        print( arg_string )

        ret = func(*args,**kwargs)
        return ret
    return _print_args




################################################################################
#                                 SUMMARY
################################################################################


def arrsummary(arr):
    """returns a Summarizer object for the given array"""
    return Summarizer(arr)

class Summarizer(dict):
    """
    Summarization object for numpy array. The primary job of this
    object is to streamline and simply printing out numpy array objects
    which normally appear as a stream of barely comprehendable data

    This dictionary subclass will return the following when printed out
    or otherwise stringified

    Args:
        input_array (np.ndarray): input array to summarize

    Attributes:
        input_array: original numpy array this object is summarizing
        last_summary: last calculated summary dictionary
                contains the following: shape, size, max, min, mean, dtype
        last_string: last representation string calculated for this array


    Example:
        >>> import imagepypelines as ip
        >>> import numpy as np
        >>> np.random.seed(0)
        >>> a = np.random.rand(512,512)
        >>> a = ip.util.Summarizer(a)
        >>> print(a)
        [ARRAY SUMMARY | shape: (512, 512) | size: 262144 | max: 1.0 | min: 0.0 | mean: 0.5 | dtype: float64]
    """
    def __init__(self, input_array):
        """Instantiation function

        Args:
            input_array (np.ndarray): input array to summarize

        """
        # ERROR CHECKING
        if not isinstance(input_array, np.ndarray):
            error_msg = "'input_array' input must be a np.ndarray"
            raise TypeError(error_msg)
        # END ERROR CHECKING
        self.input_array = input_array
        self.last_summary = None
        self.last_string = None
        self.__update()

    def __str__(self):
        """returns a stringified summary"""
        self.__update()
        return self.last_string

    def summarize(self):
        """returns an output dictionary of array attributes

        Args:
            None

        Returns:
            summary (dict): dict containing the following [shape, size, max,
                min, mean, dtype]
        """

        self.__update()
        return self.last_summary

    def __update(self):
        """
        updates the last_summary and last_string internal attributes
        """
        summary = {
        'shape': self.input_array.shape,
        'size': self.input_array.size,
        'max': round(self.input_array.max(), 3),
        'min': round(self.input_array.min(), 3),
        'mean': round(self.input_array.mean(), 3),
        'dtype': self.input_array.dtype,
        }

        string = "[ARRAY SUMMARY | "  \
                + "shape: {shape} | " \
                + "size: {size} | " \
                + "max: {max} | " \
                + "min: {min} | " \
                + "mean: {mean} | " \
                + "dtype: {dtype}]"

        string = string.format( **summary )

        self.last_summary = summary
        self.last_string = string

        self.update(self.last_summary)


    def __repr__(self):
        return str(self)


################################################################################
#                                 TIMING
################################################################################

def timer(func):
    """Decorator to time how long a func takes to run in milliseconds

    Example:
        >>> import imagepypelines as ip
        >>> import time
        >>>
        >>> @ip.timer
        ... def sleep_for_one_sec():
        ...    time.sleep(1) #sleep for 1 second
        >>>
        >>> sleep_for_one_sec() # doctest: +ELLIPSIS
        ...
    """
    def _timer(*args,**kwargs):
        t = Time()
        ret = func(*args,**kwargs)
        run_time = t.time()
        msg = "ran function '{name}' in {t}sec".format(name=func.__name__,
                                                            t=run_time)
        TIMER_LOGGER.info(msg)

        return ret

    return _timer


def timer_ms(func):
    """Decorator to time how long a func takes to run in milliseconds

    Example:
        >>> import imagepypelines as ip
        >>> import time
        >>>
        >>> @ip.timer_ms
        ... def sleep_for_one_sec():
        ...    time.sleep(1) #sleep for 1 second
        >>>
        >>> sleep_for_one_sec() # doctest: +ELLIPSIS
        ...
    """
    def _timer_ms(*args,**kwargs):
        t = Time()
        ret = func(*args,**kwargs)
        run_time_ms = t.time_ms
        msg = "ran function '{name}' in {t}ms".format(name=func.__name__,
                                                            t=run_time_ms)
        TIMER_LOGGER.info(msg)

        return ret

    return _timer_ms



class Timer(object):
    """
    Timer which can be used to time processes

    Attributes:
        _start (float): start time in seconds since the epoch
        _last (float): last time the lap timer was called
        _countdown (float): countdown time if set (recalculated with
                            the countdown property)
        _last_countdown (float): last countdown time check

    Example:
        #we need to do an action for 10 seconds
        timer = Timer()
        timer.countdown = 10

        while timer.countdown:
            do_action()
            #this action will run for (about) 10 seconds


        # maybe we want to record how long a part of our code runs
        timer.reset()

        do_action()
        print( timer.lap() )

        do_action2()
        print( timer.lap() )


    """
    def __init__(self):
        self._start = time.time()
        self._last = self._start

        self._countdown_timer = None
        self._countdown_start = None


    def reset(self):
        """ resets the timer start time """
        self.__init__()

    def time(self):
        """returns the time in seconds since the timer started or since it was
         last reset"""
        return round(self.raw_time(),3)

    def raw_time(self):
        """returns the unrounded time in seconds since the timer started"""
        return time.time() - self._start

    def lap(self):
        """returns time in seconds since last time the lap was called"""
        now = time.time()
        lap = now - self._last
        self._last = now
        return round(lap,3)

    def time_ms(self):
        """returns the time in milliseonds since the timer started or since it
        was last reset"""
        return round(self.raw_time()*1000,3)

    def lap_ms(self):
        """returns time in milliseconds since last time the lap was called"""
        return round(self.lap()*1000,3)


    @property
    def countdown(self):
        if self._countdown_timer is None:
            return 0

        countdown = self._countdown_start - self._countdown_timer.raw_time()
        countdown = max(countdown,0)
        return countdown


    @countdown.setter
    def countdown(self,value):
        """sets the countdown timer"""
        if not isinstance(value,(int,float)):
            error_msg = "countdown must be set using a float \
                        or an int, current type is {0}".format(type(value))
            core.error(error_msg)
            raise TypeError(error_msg)

        self._countdown_timer = Timer()
        self._countdown_start = float(value)


    @property
    def start(self):
        return self._start


    def __str__(self):
        return "Timer @{}sec".format( self.time() )

    def __repr__(self):
        return str(self)
