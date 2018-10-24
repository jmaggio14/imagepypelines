#!/usr/bin/env python

"""
Adds testing functions in this file, any functions you write will
be automatically run
    -JM
"""
from __future__ import print_function

import imsciutils as iu
VERBOSE = False

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
def test_linear_svm():
    import imsciutils as iu

    resizer = iu.Resizer(32,32) #28x28
    features = iu.PretrainedNetwork() # generate features
    pca = iu.PCA(256)
    classifier = iu.LinearSvm()

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
def test_linear_svm():
    import imsciutils as iu

    resizer = iu.Resizer(32,32) #28x28
    features = iu.PretrainedNetwork() # generate features
    pca = iu.PCA(256)
    classifier = iu.LinearSvm()

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
def test_rbf_svm():
    import imsciutils as iu

    resizer = iu.Resizer(32,32) #28x28
    features = iu.PretrainedNetwork() # generate features
    pca = iu.PCA(256)
    classifier = iu.RbfSvm()

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
def test_poly_svm():
    import imsciutils as iu

    resizer = iu.Resizer(32,32) #28x28
    features = iu.PretrainedNetwork() # generate features
    pca = iu.PCA(256)
    classifier = iu.PolySvm()

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
def test_sigmoid_svm():
    import imsciutils as iu

    resizer = iu.Resizer(32,32) #28x28
    features = iu.PretrainedNetwork() # generate features
    pca = iu.PCA(256)
    classifier = iu.SigmoidSvm()

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

PREVENT_TIMEOUT = True
def prevent_travis_timeout():
    import time
    global PREVENT_TIMEOUT
    while PREVENT_TIMEOUT:
        print("this message prints every 5 minutes to prevent travis-ci from auto-ending the tests")
        time.sleep(5*60)

import queue
q = queue.Queue()

def prevent_travis_timeout(q):
    import time
    val = True
    while val:
        if not q.empty():
            val = q.get(block=False)
        print("this message prints every 5 minutes to prevent travis-ci from auto-ending the tests")
        time.sleep(5*60)

def main(verbose=False):
    """
    runs all other function in this file automatically and prints out success
    or failure
    """
    import imsciutils as iu
    import six
    import threading
    import queue


    q = queue.Queue()
    travis_idle_thread = threading.Thread(target=prevent_travis_timeout,
                                                    args=(q,))
    travis_idle_thread.start()



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
        if test_func.__name__ in ['main','prevent_travis_timeout']:
            # skipping main function to avoid recursion loop
            continue
        else:
            success.append( test_func() )

    print("putting False in queue")
    q.put(False)

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
