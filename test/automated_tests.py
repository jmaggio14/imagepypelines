#!/usr/bin/env python

"""
Adds testing functions in this file, any functions you write will
be automatically run
    -JM
"""
from __future__ import print_function

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
def test_imageloader_resizer_color2gray_orb_pipeline():
    import imsciutils as iu
    import numpy as np
    testing_printer = iu.get_printer('test_imageloader_resizer_color2gray_orb_pipeline')
    ORB_KEYPOINTS = 10
    # creating all the blocks for the pipeline
    image_loader = iu.ImageLoader()
    resizer = iu.Resizer(to_height=512,to_width=512)
    color2gray = iu.Color2Gray('rgb')
    orb = iu.Orb(n_keypoints=ORB_KEYPOINTS)

    # creating pipeline with all blocks
    pipeline = iu.Pipeline(name='test_imageloader_resizer_color2gray_orb_pipeline',
                            blocks=[image_loader,resizer,color2gray,orb],
                            enable_text_graph=True)
    pipeline.printer.set_log_level('debug')
    iu.set_global_printout_level(0)

    # getting sample data for this system
    standard_image_filenames = iu.standard_image_filenames()
    processed = pipeline.process(standard_image_filenames)

    if all(p.shape == (ORB_KEYPOINTS,32) for p in processed):
        return True
    else:
        testing_printer.info("incorrect shape of outputs")
        return False


@iu.unit_test
def test_imageloader_resizer_color2gray_orb_pipeline():
    import imsciutils as iu
    import numpy as np
    testing_printer = iu.get_printer('test_imageloader_resizer_color2gray_orb_pipeline')
    ORB_KEYPOINTS = 10
    # creating all the blocks for the pipeline
    image_loader = iu.ImageLoader()
    resizer = iu.Resizer(to_height=512,to_width=512)
    color2gray = iu.Color2Gray('rgb')
    orb = iu.Orb(n_keypoints=ORB_KEYPOINTS)

    # creating pipeline with all blocks
    pipeline = iu.Pipeline(name='test_imageloader_resizer_color2gray_orb_pipeline',
                            blocks=[image_loader,resizer,color2gray,orb],
                            enable_text_graph=True).debug()
    pipeline.printer.set_log_level('debug')
    iu.set_global_printout_level(0)

    # getting sample data for this system
    standard_image_filenames = iu.standard_image_filenames()
    processed = pipeline.process(standard_image_filenames)

    if all(p.shape == (ORB_KEYPOINTS,32) for p in processed):
        return True
    else:
        testing_printer.info("incorrect shape of outputs")
        return False


@iu.unit_test
def test_multilayer_perceptron():
    import imsciutils as iu

    resizer = iu.Resizer(32,32) #28x28
    features = iu.PretrainedNetwork() # generate features
    pca = iu.PCA(256)
    classifier = iu.MultilayerPerceptron(neurons=512,
                                            validation=.1,
                                            num_hidden=3,
                                            dropout=.35,
                                            learning_rate=.01) # NN classifier
    # there are a lot more parameters you can tweak!

    pipeline = iu.Pipeline([resizer,features,pca,classifier]).debug()

    # for this example, we'll need to load the standard Mnist handwriting dataset
    # built into `imsciutils`
    mnist = iu.Mnist()
    train_data, train_labels = mnist.get_train()
    test_data, ground_truth = mnist.get_test()

    # train the classifier
    pipeline.train(train_data,train_labels)

    # test the classifier
    predictions = pipeline.process(test_data)

    # print the accuracy
    accuracy = iu.accuracy(predictions,ground_truth)
    print('accuracy is ', accuracy)

    if len(predictions) == len(test_data):
        return True
    return False

@iu.unit_test
def test_all_pretrained_networks():
    import imsciutils as iu
    import cv2

    filenames = iu.standard_image_filenames()
    images = [cv2.imread(f,cv2.IMREAD_COLOR) for f in filenames]
    printer = iu.get_printer('test_all_pretrained_networks')

    success = []
    for i,network_name in enumerate(iu.PRETRAINED_NETWORKS):
        try:
            printer.info("testing {}...".format(network_name))
            resizer = iu.Resizer(80,80)
            pretrained = iu.PretrainedNetwork(network_name)

            pipeline = iu.Pipeline([resizer,pretrained])
            pipeline.process(images)

            del pretrained
            del pipeline
            success.append(True)
            printer.info("{}/{} test successful!"\
                            .format(i+1,len(iu.PRETRAINED_NETWORKS)))


        except Exception as e:
            printer.error("failure processing ",network_name)
            success.append(False)

    return all(success)








def main(verbose=False):
    """
    runs all other function in this file automatically and prints out success
    or failure
    """
    import imsciutils as iu
    import six

    if verbose:
        if six.PY2:
            print('verbose options are not available in python2!')
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
