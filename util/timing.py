#
# marvin (c) by Jeffrey Maggio, Hunter Mellema, Joseph Bartelmo
#
# marvin is licensed under a
# Creative Commons Attribution-ShareAlike 4.0 International License.
#
# You should have received a copy of the license along with this
# work. If not, see <http://creativecommons.org/licenses/by-sa/4.0/>.
#
#
import time
import imsciutils


def function_timer(func):
    """
    Decorator to time how long a func takes to run in seconds

    EXAMPLE:
        @function_timer
        def sleep_for_one_sec:
            time.sleep(1)#sleep for 1 second

        >>> sleep_for_one_sec
        (imsciutils)(info) ran func 'sleep_for_one_sec' in 1.030sec
    """
    def _function_timer(*args,**kwargs):
        start = time.time()
        ret = func(*args,**kwargs)
        run_time = round(time.time() - start,3)
        msg = "ran function '{name}' in {t}sec".format(name=func.__name__,
                                                            t=run_time)
        imsciutils.info(msg)

        return ret

    return _function_timer


def function_timer_ms(func):
    """
    Decorator to time how long a func takes to run in milliseconds

    EXAMPLE:
        @function_timer
        def sleep_for_one_sec:
            time.sleep(1)#sleep for 1 second

        >>> sleep_for_one_sec
        (imsciutils)(info) ran func 'sleep_for_one_sec' in 1005.28ms
    """
    def _function_timer(*args,**kwargs):
        start = time.time()
        ret = func(*args,**kwargs)
        run_time = round(time.time() - start,5) * 1000
        msg = "ran function '{name}' in {t}ms".format(name=func.__name__,
                                                            t=run_time)
        imsciutils.info(msg)

        return ret

    return _function_timer



class Timer(object):
    """
    Timer which can be used to time processes

    attributes::
        _start (float): start time in seconds since the epoch
        _last (float): last time the lap timer was called
        _countdown (float): countdown time if set (recalculated with
                            the countdown property)
        _last_countdown (float): last countdown time check

    functions::
        reset(): resets the timer (runs __init__())
        time(): time since the timer started or was last reset
        lap(): time since lap was last accessed (or when timer was created
        for the first access)

    properties::
        countdown: countdown time, recalculated every time it's called.
                        never below 0
        countdown.setter: sets the value of countdown


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

        self._last_countdown = float(0)
        self._countdown = float(0)


    def reset(self):
        """ resets the timer start time """
        self.__init__()

    def time(self):
        """returns the time since the timer started or since it was
         last reset"""
        return time.time() - self._start

    def lap(self):
        """returns time since last time the lap was called"""
        now = time.time()
        lap = now - self._last
        self._last = now
        return lap

    @property
    def countdown(self):
        """returns the current countdown time"""
        self._countdown = self._countdown - (self.time - self._last_countdown)
        self._last_countdown = self.time
        if self._countdown < 0:
            self._countdown = 0
        return self._countdown

    @countdown.setter
    def countdown(self,value):
        """sets the countdown timer"""
        if isinstance(value,(int,float)):
            self._countdown = float(value)
        else:
            imsciutils.error("countdown must be set using a float \
                    or an int, current type is {0}".format(type(value)))

    @property
    def start(self):
        return self._start
