#!/usr/bin/env python

"""
Adds testing functions in this file, any functions you write will
be automatically run
    -JM
"""
from __future__ import print_function

import imagepypelines as ip
VERBOSE = False
# constants.py
@ip.util.unit_test
def test_constants():
    import imagepypelines as ip
    testing_printer = ip.get_printer('test_constants')
    if not 'CV2_INTERPOLATION_TYPES' in dir(ip):
        return False
    if not 'NUMPY_TYPES' in dir(ip):
        return False
    if not 'IMAGE_EXTENSIONS' in dir(ip):
        return False
    if not 'PRETRAINED_NETWORKS' in dir(ip):
        return False

    return True


# coordinates.py
@ip.util.unit_test
def test_centroid():
    import imagepypelines as ip
    testing_printer = ip.get_printer('test_centroid')
    tester = ip.util.Tester(ip.centroid,verbose=VERBOSE)
    lenna = ip.lenna()
    desired_output = (256,256)
    if not tester.exact_test(desired_output, lenna):
        return False

    return True


@ip.util.unit_test
def test_frame_size():
    import imagepypelines as ip
    testing_printer = ip.get_printer('test_frame_size')
    tester = ip.util.Tester(ip.frame_size,verbose=VERBOSE)
    lenna = ip.lenna()
    desired_output = tuple( lenna.shape[:2] )
    if not tester.exact_test(desired_output,lenna):
        return False

    return True


@ip.util.unit_test
def test_dimensions():
    import imagepypelines as ip
    testing_printer = ip.get_printer('test_dimensions')
    tester = ip.util.Tester(ip.dimensions,verbose=VERBOSE)
    lenna = ip.lenna()
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
@ip.util.unit_test
def test_normalize_and_bin():
    import imagepypelines as ip
    import numpy as np
    testing_printer = ip.get_printer('test_normalize_and_bin')
    tester = ip.util.Tester(ip.normalize_and_bin,verbose=VERBOSE)
    lenna = ip.lenna()
    desired_output = np.uint8(lenna.astype(np.float32) / lenna.max() * 255)
    if not tester.exact_test(desired_output,lenna):
        return False

    return True



@ip.util.unit_test
def test_imageloader_resizer_color2gray_orb_pipeline():
    import imagepypelines as ip
    import numpy as np
    testing_printer = ip.get_printer('test_imageloader_resizer_color2gray_orb_pipeline')
    ORB_KEYPOINTS = 10
    # creating all the blocks for the pipeline
    image_loader = ip.blocks.ImageLoader()
    resizer = ip.blocks.Resizer(to_height=512,to_width=512)
    color2gray = ip.blocks.Color2Gray('rgb')
    orb = ip.blocks.Orb(n_keypoints=ORB_KEYPOINTS)

    # creating pipeline with all blocks
    pipeline = ip.Pipeline(name='test_imageloader_resizer_color2gray_orb_pipeline',
                            blocks=[image_loader,resizer,color2gray,orb],
                            enable_text_graph=True)
    pipeline.printer.set_log_level('debug')
    ip.set_global_printout_level(0)

    # getting sample data for this system
    standard_image_filenames = ip.standard_image_filenames()
    processed = pipeline.process(standard_image_filenames)

    if all(p.shape == (ORB_KEYPOINTS,32) for p in processed):
        return True
    else:
        testing_printer.info("incorrect shape of outputs")
        return False


@ip.util.unit_test
def test_imageloader_resizer_color2gray_orb_pipeline():
    import imagepypelines as ip
    import numpy as np
    testing_printer = ip.get_printer('test_imageloader_resizer_color2gray_orb_pipeline')
    ORB_KEYPOINTS = 10
    # creating all the blocks for the pipeline
    image_loader = ip.blocks.ImageLoader()
    resizer = ip.blocks.Resizer(to_height=512,to_width=512)
    color2gray = ip.blocks.Color2Gray('rgb')
    orb = ip.blocks.Orb(n_keypoints=ORB_KEYPOINTS)

    # creating pipeline with all blocks
    pipeline = ip.Pipeline(name='test_imageloader_resizer_color2gray_orb_pipeline',
                            blocks=[image_loader,resizer,color2gray,orb],
                            enable_text_graph=True).debug()
    pipeline.printer.set_log_level('debug')
    ip.set_global_printout_level(0)

    # getting sample data for this system
    standard_image_filenames = ip.standard_image_filenames()
    processed = pipeline.process(standard_image_filenames)

    if all(p.shape == (ORB_KEYPOINTS,32) for p in processed):
        return True
    else:
        testing_printer.info("incorrect shape of outputs")
        return False


# @ip.util.unit_test
# def test_caching():
#     import imagepypelines as ip
#     import numpy as np
#     import cv2
#
#     # save an object to the builtin 'tmp' cache
#     a = "this is an example object" # this is an example object
#     fname = ip.tmp.save(a)
#     restored_a = ip.tmp.restore(fname)
#     assert a == restored_a, "failed to restore '{}'".format(a)
#
#     #---- make an example cache -----
#     ip.make_cache('example_cache')
#     # we can now access the cache via ip.example_cache
#     assert hasattr(ip,'example_cache'),"failed to create example_cache"
#
#
#     # get a unique cache filename, so you can do your own saving process
#     fname = ip.example_cache.filename('example-image.png')
#     img = np.random.rand(512,512,3)
#     cv2.imwrite(fname,img)



# @ip.util.unit_test
# def test_thresholding_otsu():
#     import imagepypelines as ip
#     import os
#
#     testing_printer = ip.get_printer('otsu_thresholding')
#
#     standard_image_filenames = ip.standard_image_filenames()
#
#     # build blocks for this pipeline
#     loader = ip.ImageLoader()
#     gray2color = ip.Gray2Color()
#     otsu = ip.Otsu()
#     writer = ip.WriterBlock('./output_dir',return_type='filename')
#
#     # pipeline construction
#     pipeline = ip.Pipeline([loader,gray2color,otsu,writer])
#
#     # get filenames of saved thresholded data
#     processed_filenames = pipeline.process(standard_image_filenames)
#
#     for fname in processed_filenames:
#         if not os.path.exists(fname):
#             testing_printer.info("{} was not properly saved".format(fname))
import six
if six.PY3:
    import queue
else:
    import Queue as queue

Q = queue.Queue()

def prevent_travis_timeout():
    import time
    import sys
    from datetime import datetime

    exit_status = False
    idx = 0
    while True:
        if not idx % 300 or idx == 0:
            print("{} : this message is printed to prevent travis from timing out the test".format(datetime.now()))

        #check queue
        if not Q.empty():
            exit_status = Q.get_nowait()

        if exit_status:
            sys.exit()

        time.sleep(1) # sleep for 5minutes
        idx += 1



def main(verbose=False):
    """
    runs all other function in this file automatically and prints out success
    or failure
    """
    import imagepypelines as ip
    import six
    import threading

    travis_timeout = threading.Thread(target=prevent_travis_timeout)
    travis_timeout.start()

    if verbose:
        if six.PY2:
            print('verbose options are not available in python2!')
        else:
            global VERBOSE
            VERBOSE = True
    else:
        ip.disable_all_printers()

    import sys
    unit_tests = [var for var in globals().values() if callable(var)]
    success = []
    for test_func in unit_tests:
        if test_func.__name__ in ['main','prevent_travis_timeout']:
            # skipping main function to avoid recursion loop
            continue
        else:
            success.append( test_func() )

    print("tests completed!")
    print("closing travis timeout thread...")
    Q.put_nowait(True) #tell the travis thread to exit

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
