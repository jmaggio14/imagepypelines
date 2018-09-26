#!/usr/bin/env python

"""
Adds testing functions in this file, any functions you write will
be automatically run
    -JM
"""

import imsciutils as iu

# constants.py
@iu.unit_test
def test_constants():
    import imsciutils as iu
    testing_printer = iu.get_printer('test_constants')
    if not 'CV2_INTERPOLATION_TYPES' in dir(iu):
        return False
    if not 'NUMPY_TYPES' in dir(iu):
        return False
    if not 'IMAGE_EXTENSIONS' in dir(iu):
        return False

    return True


# coordinates.py
@iu.unit_test
def test_centroid():
    import imsciutils as iu
    testing_printer = iu.get_printer('test_centroid')
    tester = iu.Tester(iu.centroid,verbose=False)
    lenna = iu.lenna()
    desired_output = (256,256)
    if not tester.exact_test(desired_output, lenna):
        return False

    return True


@iu.unit_test
def test_frame_size():
    import imsciutils as iu
    testing_printer = iu.get_printer('test_frame_size')
    tester = iu.Tester(iu.frame_size,verbose=False)
    lenna = iu.lenna()
    desired_output = tuple( lenna.shape[:2] )
    if not tester.exact_test(desired_output,lenna):
        return False

    return True


@iu.unit_test
def test_dimensions():
    import imsciutils as iu
    testing_printer = iu.get_printer('test_dimensions')
    tester = iu.Tester(iu.dimensions,verbose=False)
    lenna = iu.lenna()
    # tuple test
    desired_output = (lenna.shape[0],lenna.shape[1],lenna.shape[2],lenna.dtype)
    if not tester.exact_test(desired_output,lenna):
        return False
    # dimensions test
    desired_output = {
                        'rows':lenna.shape[0],
                        'cols':lenna.shape[1],
                        'bands':lenna.shape[2],
                        'dtype':lenna.dtype,
                        }
    if not tester.exact_test(desired_output,lenna,return_as_dict=True):
        return False

    return True



# img_tools.py
@iu.unit_test
def test_normalize_and_bin():
    import imsciutils as iu
    import numpy as np
    testing_printer = iu.get_printer('test_normalize_and_bin')
    tester = iu.Tester(iu.normalize_and_bin,verbose=False)
    lenna = iu.lenna()
    desired_output = np.uint8(lenna.astype(np.float32) / lenna.max() * 255)
    if not tester.exact_test(desired_output,lenna):
        return False

    return True









def main():
    """
    runs all other function in this file automatically and prints out success
    or failure
    """
    import sys
    print('running main')
    unit_tests = [var for var in globals().values() if callable(var)]
    import imsciutils as iu
    iu.disable_all_printers()
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
    main()






# END
