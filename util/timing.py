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
import imsciutils as iu


def function_timer(func):
    """
    Decorator to time how long a func takes to run in seconds

    EXAMPLE:
        @function_timer
        def sleep_for_one_sec():
            time.sleep(1) # sleep for 1 second

        >>> sleep_for_one_sec()
        (  function_timer  )[    INFO    ] ran function '_function_timer' in 1.001sec
    """
    printer = iu.get_printer('function_timer')
    def _function_timer(*args,**kwargs):
        start = time.time()
        ret = func(*args,**kwargs)
        run_time = round(time.time() - start,3)
        msg = "ran function '{name}' in {t}sec".format(name=func.__name__,
                                                            t=run_time)
        printer.info(msg)

        return ret

    return _function_timer


def function_timer_ms(func):
    """
    Decorator to time how long a func takes to run in milliseconds

    EXAMPLE:
        @function_timer
        def sleep_for_one_sec():
            time.sleep(1) #sleep for 1 second

        >>> sleep_for_one_sec()
        (  function_timer  )[    INFO    ] ran function 'sleep_for_one_sec' in 1000.118ms
    """
    printer = iu.get_printer('function_timer')
    def _function_timer(*args,**kwargs):
        start = time.time()
        ret = func(*args,**kwargs)
        run_time = round((time.time() - start) * 1000,3)
        msg = "ran function '{name}' in {t}ms".format(name=func.__name__,
                                                            t=run_time)
        printer.info(msg)

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

        self._countdown_timer = None
        self._countdown_start = None


    def reset(self):
        """ resets the timer start time """
        self.__init__()

    def time(self):
        """returns the time since the timer started or since it was
         last reset"""
        return round(self.raw_time(),3)

    def raw_time(self):
        """returns the unrounded time since the timer started"""
        return time.time() - self._start

    def lap(self):
        """returns time since last time the lap was called"""
        now = time.time()
        lap = now - self._last
        self._last = now
        return round(lap,3)

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
            iu.error(error_msg)
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


def main():
    import time
    import imsciutils as iu

    @iu.util.function_timer
    @iu.util.function_timer_ms
    def sleep_for_one_sec():
        time.sleep(1)

    t = iu.util.Timer()
    sleep_for_one_sec()
    print( t.lap() )

    @iu.util.function_timer
    def _check_countdown(countdown_time):
        t.countdown = countdown_time
        while t.countdown:
            pass

    _check_countdown(10)
    _check_countdown(20)
    _check_countdown(30)
            # print("real:",30 - t.time(),' countdown:',t.countdown)




if __name__ == "__main__":
    main()
