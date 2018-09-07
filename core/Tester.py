import imsciutils as iu
import numpy as np
import inspect
from collections import Iterable


class Tester(object):
    """
    Testing object used to simply unit testing for a target function. This object
    can perform exact and type check tests on a target function and interally
    w


    """
    def __init__(self, target, verbose=True):
        if not callable(target):
            error_msg = "'target' must be a callable class or function!"
            iu.error(error_msg)
            raise TypeError(error_msg)

        self.target = target
        self.verbose = verbose  # Unused


    def __str__(self):
        return "[imsciutils Tester for '{}' function]".format(self.target.__name__)

    def __repr__(self):
        return self.__str__()

    def exact_test(self, desired_output, *args, **kwargs):
        # printing out args and kwargs if desired by user
        if self.verbose:
            print("----------TESTING '{}'----------".format(self.target.__name__))
            self.__print_args(*args,**kwargs)


        # running the target with a debug wrapper
        out = self.__run_target(*args,**kwargs)

        # testing the output
        if iu.is_numpy_array(out) and iu.is_numpy_array(desired_output):
            has_failed = not np.all(out == desired_output)
        else:
            has_failed = (out != desired_output)


        if has_failed:
            # TEST HAS FAILED
            # converting to any numpy arrays to summaries for printout
            if iu.is_numpy_array(desired_output):
                desired_output = iu.util.Summarizer(desired_output)
            if iu.is_numpy_array(out):
                out = iu.util.Summarizer(out)

            iu.error("{} test failure expected output {}, but got {}"\
                            .format(self.target.__name__,desired_output, out))
            return False
        else:
            # TEST HAS SUCEEDED
            iu.printmsg("{} exact test success!".format(self.target.__name__))
            return True


    def type_test(self,desired_type,*args,**kwargs):
        """
        Checks whether the target function outputs the correct type or types
        given a set of args and kwargs

        Input::
            desired_type (type or iterable of types): the type or types the output
                function should return

        EXAMPLE:
        def output_str_or_int(a):
            if a:
                return "1"
            else:
                return 1

        tester = Tester(output_str_or_int)
        is_test_successful = tester.type_test(str, a=True)

        # outputs True or False depending on whether the test was passed
        """
        # Making desired_type a list if it isn't already
        if not isinstance(desired_type,Iterable):
            desired_type = [desired_type]

        # print out args and kwargs if desired
        if self.verbose:
            print("--------TESTING '{}'--------".format(self.target.__name__))
            self.__print_args(*args,**kwargs)

        # run the target function
        out = self.__run_target(*args,**kwargs)

        # testing the output
        if not isinstance(out,tuple(desired_type)):
            # TEST HAS FAILED
            iu.error("{} test failure expected output {}, but got {}"\
                        .format(self.target.__name__,desired_type, type(out)))

            return False
        else:
            # TEST HAS SUCEEDED
            iu.printmsg("{} type test successful! with type {}!"\
                            .format(self.target.__name__,type(out)))
            return True




    def __print_args(self,*args,**kwargs):
        """
        prints the arguments passed into the target
        """
        iu.info("testing function '{}' with the following args:"\
                                                .format(self.target.__name__))
        arg_string = ""
        arg_names = inspect.getfullargspec(self.target).args
        # adds positional arguments to the printout
        for i, arg in enumerate(args):
            # summarizing an numpy array so prinout is more concise
            if iu.is_numpy_array(arg):
                arg = str(iu.Summarizer(arg))
            arg_string += '\t{} : {}\n'.format(arg_names[i], arg)

        # adds keyword arguments to the printout
        for key, val in kwargs.items():
            # summarizing an numpy array so printout is more concise
            if iu.is_numpy_array(val):
                val = str( iu.Summarizer(val) )

            arg_string += '\t{} : {}\n'.format(key, val)

        print(arg_string)


    def __run_target(self,*args,**kwargs):
        # testing to make sure the function will run
        try:
            out = self.target(*args, *kwargs)
            return out
        except Exception as e:
            iu.error("{} test failed to run!".format(self.target.__name__))
            iu.util.debug(e)



def main():
    def test_target(a, b, c, ryanisdumb):
        return a

    tester = Tester(test_target)
    desired_output = False
    tester.exact_test(desired_output, True, iu.lenna(), None, ryanisdumb="yes")
    tester.type_test(bool, True, iu.lenna(), None, ryanisdumb="yes")



if __name__ == "__main__":
    main()
