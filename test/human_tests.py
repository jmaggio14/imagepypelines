import imagepypelines as ip

ip.util.human_test
def test_quick_image_view():
    """THIS TEST REQUIRES A HUMAN TO VIEW THE IMAGE"""
    import imagepypelines as ip
    testing_printer = ip.get_printer('test_quick_image_view')

    pig = ip.pig()
    ip.quick_image_view(pig,title='quick_image_view test')


ip.util.human_test
def test_number_image():
    import imagepypelines as ip
    testing_printer = ip.get_printer('test_number_image')

    pig = ip.pig()
    linear = ip.linear()

    num_pig = ip.number_image(pig,1)
    testing_printer.info("pig should be labeled '1'")
    num_linear = ip.number_image(linear,2)
    testing_printer.info("linear should be labeled '2'")

    ip.quick_image_view(pig,title='pig')
    testing_printer.info('PIG', ip.Summarizer(pig) )
    ip.quick_image_view(linear,title='linear')
    testing_printer.info('Linear', ip.Summarizer(linear) )

ip.util.human_test
def test_imageloader_resizer_color2gray_viewer_orb_pipeline():
    import imagepypelines as ip
    import numpy as np
    testing_printer = ip.get_printer('imageloader->resizer->color2gray->viewer->orb')
    ORB_KEYPOINTS = 10
    # creating all the blocks for the pipeline
    image_loader = ip.ImageLoader()
    resizer = ip.Resizer(to_height=512,to_width=512)
    color2gray = ip.Color2Gray('rgb')
    viewer = ip.BlockViewer()
    orb = ip.Orb(n_keypoints=ORB_KEYPOINTS)

    # creating pipeline with all blocks
    pipeline = ip.Pipeline(name=None,
                            blocks=[image_loader,resizer,viewer,color2gray,orb])


    # getting sample data for this system
    standard_image_filenames = ip.standard_image_filenames()
    processed = pipeline.process(standard_image_filenames)

ip.util.human_test
def test_cameracapture_viewer_pipeline():
    import imagepypelines as ip
    testing_printer = ip.get_printer('cameracapture->viewer')

    capture = ip.CameraBlock(mode='time')
    viewer = ip.BlockViewer()

    pipeline = ip.Pipeline()
    pipeline.add(capture)
    pipeline.add(viewer)


    #capture for 30 seconds
    images = pipeline.process( [30] )






def main(verbose=False):
    """
    runs all other function in this file automatically and prints out success
    or failure
    """
    import imagepypelines as ip
    import six

    if verbose:
        if six.PY2:
            print('verbose options are not available in python2')
        else:
            global VERBOSE
            VERBOSE = True
    else:
        ip.disable_all_printers()

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
    parser.add_argument('--quiet-mode',
                        help='whether or not to print out the arguments passed into functions that use Tester',
                        action='store_true')
    args = parser.parse_args()
    main(not args.quiet_mode)
