import imsciutils as iu
import numpy as np
import inspect
from collections import Iterable


class Tester(object):
    """
    """
    def __init__(self, target, verbose=True):
        if not callable(target):
            error_msg = "'target' must be a callable class or function!"
            iu.error(error_msg)
            raise TypeError(error_msg)

        self.target = target
        self.verbose = verbose  # Unused

    def exact_test(self, desired_output, *args, **kwargs):
        if self.verbose:
            print("----------TESTING '{}'----------".format(self.target.__name__))
            self.__print_args(*args,**kwargs)
        # running the target with a debug wrapper
        out = self.__run_target(*args,**kwargs)

        # testing the output
        if iu.util.is_numpy_array(out) and iu.util.is_numpy_array(desired_output):
            failure_criterion = np.any(out != desired_output)
        else:
            failure_criterion = (out != desired_output)

        if failure_criterion:
            # converting to any numpy arrays to summaries for printout
            if iu.util.is_numpy_array(desired_output):
                desired_output = iu.util.Summarizer(desired_output)
            if iu.util.is_numpy_array(out):
                out = iu.util.Summarizer(out)

            iu.error("{} test failure expected output {}, but got {}"\
                            .format(self.target.__name__,desired_output, out))
            return False
        else:
            iu.printmsg("{} exact test success!".format(self.target.__name__))
            return True


    def type_test(self,desired_type,*args,**kwargs):
        if not isinstance(desired_type,Iterable):
            desired_type = [desired_type]

        if self.verbose:
            print("--------TESTING '{}'--------".format(self.target.__name__))
            self.__print_args(*args,**kwargs)


        out = self.__run_target(*args,**kwargs)

        # testing the output
        if out in desired_type:
            iu.error("{} test failure expected output {}, but got {}"\
                        .format(self.target.__name__,desired_type, type(out)))

            return False
        else:
            iu.printmsg("{} type test successful! with type {}!"\
                            .format(self.target.__name__,type(out)))
            return True




    def __print_args(self,*args,**kwargs):
        """
        prints the arguments passed into the 
        """
        iu.printmsg("testing function '{}' with the following args:"\
                                                .format(self.target.__name__))
        arg_string = ""
        arg_names = inspect.getfullargspec(self.target).args
        # adds positional arguments to the printout
        for i, arg in enumerate(args):
            # summarizing an numpy array so prinout is more concise
            if iu.util.is_numpy_array(arg):
                arg = str(iu.Summarizer(arg))
            arg_string += '\t{} : {}\n'.format(arg_names[i], arg)

        # adds keyword arguments to the printout
        for key, val in kwargs.items():
            # summarizing an numpy array so prinout is more concise
            if iu.util.is_numpy_array(val):
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
