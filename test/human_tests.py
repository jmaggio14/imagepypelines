import imsciutils as iu

@iu.human_test
def test_quick_image_view():
    """THIS TEST REQUIRES A HUMAN TO VIEW THE IMAGE"""
    import imsciutils as iu
    testing_printer = iu.get_printer('test_quick_image_view')

    pig = iu.pig()
    iu.quick_image_view(pig,title='quick_image_view test')


@iu.human_test
def test_number_image():
    import imsciutils as iu
    testing_printer = iu.get_printer('test_number_image')

    pig = iu.pig()
    linear = iu.linear()

    num_pig = iu.number_image(pig,1)
    testing_printer.info("pig should be labeled '1'")
    num_linear = iu.number_image(linear,2)
    testing_printer.info("linear should be labeled '2'")

    iu.quick_image_view(pig,title='pig')
    testing_printer.info('PIG', iu.Summarizer(pig) )
    iu.quick_image_view(linear,title='linear')
    testing_printer.info('Linear', iu.Summarizer(linear) )





def main(verbose=False):
    """
    runs all other function in this file automatically and prints out success
    or failure
    """
    import imsciutils as iu
    import six

    if verbose:
        if six.PY2:
            print('verbose options are not available in python2')
        else:
            global VERBOSE
            VERBOSE = True
    else:
        iu.disable_all_printers()

    import sys
    unit_tests = [var for var in globals().values() if callable(var)]
    success = []
    for test_func in unit_tests:
        if test_func.__name__ == 'main':
            # skipping main function to avoid recursion loop
            continue
        else:
            success.append( test_func() )

    # Exit with a 1 code if more than 1 unit test failed
    sys.exit( not all(success) )


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose',
                        help='whether or not to print out the arguments passed into functions that use Tester',
                        action='store_true')
    args = parser.parse_args()
    main(args.verbose)
