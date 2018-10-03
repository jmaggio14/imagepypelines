#!/usr/bin/env python

"""
Adds testing functions in this file, any functions you write will
be automatically run
    -JM
"""

import imsciutils as iu
VERBOSE = False
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
    tester = iu.Tester(iu.centroid,verbose=VERBOSE)
    lenna = iu.lenna()
    desired_output = (256,256)
    if not tester.exact_test(desired_output, lenna):
        return False

    return True


@iu.unit_test
def test_frame_size():
    import imsciutils as iu
    testing_printer = iu.get_printer('test_frame_size')
    tester = iu.Tester(iu.frame_size,verbose=VERBOSE)
    lenna = iu.lenna()
    desired_output = tuple( lenna.shape[:2] )
    if not tester.exact_test(desired_output,lenna):
        return False

    return True


@iu.unit_test
def test_dimensions():
    import imsciutils as iu
    testing_printer = iu.get_printer('test_dimensions')
    tester = iu.Tester(iu.dimensions,verbose=VERBOSE)
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
    tester = iu.Tester(iu.normalize_and_bin,verbose=VERBOSE)
    lenna = iu.lenna()
    desired_output = np.uint8(lenna.astype(np.float32) / lenna.max() * 255)
    if not tester.exact_test(desired_output,lenna):
        return False

    return True



@iu.unit_test
def test_orb_pipeline():
    import imsciutils as iu
    import numpy as np
    testing_printer = iu.get_printer('test_orb_pipeline')
    N_KEYPOINTS = 120
    # adding orb to a pipeline
    pipeline = iu.Pipeline(name='test_orb_pipeline')
    orb = iu.ml.Orb('test_orb').setup(n_keypoints=N_KEYPOINTS)
    pipeline.add(orb)

    # loading an empty array and lenna
    lenna = iu.lenna_gray()
    lenna = lenna.reshape((1, lenna.shape[0], lenna.shape[1],1))
    empty = np.zeros(lenna.shape)

    # stacking images for pipeline
    img_stack = np.vstack( (lenna,empty) )


    # processing test
    pipeline.train(img_stack)
    des = pipeline.process(img_stack)

    # checking to make sure the empty array has zero valued descriptors
    empty_works = np.all( des[1,:,:] == 0 )
    if empty_works:
        testing_printer.info('empty array input is success')
    else:
        testing_printer.warning('empty array input is failure')

    # checking to make sure the array is the correct shape
    correct_shape = des.shape == (2,N_KEYPOINTS,32)
    if correct_shape:
        testing_printer.info('shape of output is success')
    else:
        testing_printer.warning('shape of output is failure')

    return (empty_works and correct_shape)







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
    if not all(success):
        print('not all unit tests passed. add --verbose for more details')
        sys.exit( 1 )


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose',
                        help='whether or not to print out the arguments passed into functions that use Tester',
                        action='store_true')
    args = parser.parse_args()
    main(args.verbose)






# END
