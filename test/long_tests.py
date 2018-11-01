#!/usr/bin/env python

"""
Adds testing functions in this file, any functions you write will
be automatically run
    -JM
"""
from __future__ import print_function

import imagepypelines as ip
VERBOSE = False

@ip.util.unit_test
def test_dataset_mnist():
    import imagepypelines as ip
    import numpy as np

    TRAINING_LENGTH = 60000
    TESTING_LENGTH = 10000
    NUM_LABELS = 10


    dataset = ip.Mnist()

    train_data,train_labels = dataset.get_train()
    test_data,test_labels = dataset.get_test()

    assert len(train_data) == TRAINING_LENGTH,"train data is incorrect length"
    assert len(train_labels) == TRAINING_LENGTH,"train labels is incorrect length"
    assert len(test_data) == TESTING_LENGTH,"test data is incorrect length"
    assert len(test_labels) == TESTING_LENGTH,"test labels is incorrect length"

    sorted_train_data,sorted_train_labels = dataset.get_sorted_train()
    sorted_test_data,sorted_test_labels = dataset.get_sorted_test()

    assert sorted(sorted_train_labels) == sorted_train_labels
    assert sorted(sorted_test_labels) == sorted_test_labels

    assert len(np.unique(train_labels)) == NUM_LABELS


    return True



@ip.util.unit_test
def test_dataset_mnist_fashion():
    import imagepypelines as ip
    import numpy as np

    TRAINING_LENGTH = 60000
    TESTING_LENGTH = 10000
    NUM_LABELS = 10

    dataset = ip.MnistFashion()

    train_data,train_labels = dataset.get_train()
    test_data,test_labels = dataset.get_test()

    assert len(train_data) == TRAINING_LENGTH,"train data is incorrect length"
    assert len(train_labels) == TRAINING_LENGTH,"train labels is incorrect length"
    assert len(test_data) == TESTING_LENGTH,"test data is incorrect length"
    assert len(test_labels) == TESTING_LENGTH,"test labels is incorrect length"

    sorted_train_data,sorted_train_labels = dataset.get_sorted_train()
    sorted_test_data,sorted_test_labels = dataset.get_sorted_test()

    assert sorted(sorted_train_labels) == sorted_train_labels
    assert sorted(sorted_test_labels) == sorted_test_labels

    assert len(np.unique(train_labels)) == NUM_LABELS


    return True

@ip.util.unit_test
def test_dataset_cifar10():
    import imagepypelines as ip
    import numpy as np

    TRAINING_LENGTH = 50000
    TESTING_LENGTH = 10000
    NUM_LABELS = 10

    dataset = ip.Cifar10()

    train_data,train_labels = dataset.get_train()
    test_data,test_labels = dataset.get_test()

    assert len(train_data) == TRAINING_LENGTH,"train data is incorrect length"
    assert len(train_labels) == TRAINING_LENGTH,"train labels is incorrect length"
    assert len(test_data) == TESTING_LENGTH,"test data is incorrect length"
    assert len(test_labels) == TESTING_LENGTH,"test labels is incorrect length"

    sorted_train_data,sorted_train_labels = dataset.get_sorted_train()
    sorted_test_data,sorted_test_labels = dataset.get_sorted_test()

    assert sorted(sorted_train_labels) == sorted_train_labels
    assert sorted(sorted_test_labels) == sorted_test_labels

    assert len(np.unique(train_labels)) == NUM_LABELS


    return True


@ip.util.unit_test
def test_dataset_cifar100_fine():
    import imagepypelines as ip
    import numpy as np

    TRAINING_LENGTH = 50000
    TESTING_LENGTH = 10000
    NUM_LABELS = 100

    dataset = ip.Cifar100('fine')

    train_data,train_labels = dataset.get_train()
    test_data,test_labels = dataset.get_test()

    assert len(train_data) == TRAINING_LENGTH,"train data is incorrect length"
    assert len(train_labels) == TRAINING_LENGTH,"train labels is incorrect length"
    assert len(test_data) == TESTING_LENGTH,"test data is incorrect length"
    assert len(test_labels) == TESTING_LENGTH,"test labels is incorrect length"

    sorted_train_data,sorted_train_labels = dataset.get_sorted_train()
    sorted_test_data,sorted_test_labels = dataset.get_sorted_test()

    assert sorted(sorted_train_labels) == sorted_train_labels
    assert sorted(sorted_test_labels) == sorted_test_labels

    assert len(np.unique(train_labels)) == NUM_LABELS

    return True

@ip.util.unit_test
def test_dataset_cifar100_coarse():
    import imagepypelines as ip
    import numpy as np

    TRAINING_LENGTH = 50000
    TESTING_LENGTH = 10000
    NUM_LABELS = 20

    dataset = ip.Cifar100('coarse')

    train_data,train_labels = dataset.get_train()
    test_data,test_labels = dataset.get_test()

    assert len(train_data) == TRAINING_LENGTH,"train data is incorrect length"
    assert len(train_labels) == TRAINING_LENGTH,"train labels is incorrect length"
    assert len(test_data) == TESTING_LENGTH,"test data is incorrect length"
    assert len(test_labels) == TESTING_LENGTH,"test labels is incorrect length"

    sorted_train_data,sorted_train_labels = dataset.get_sorted_train()
    sorted_test_data,sorted_test_labels = dataset.get_sorted_test()

    assert sorted(sorted_train_labels) == sorted_train_labels
    assert sorted(sorted_test_labels) == sorted_test_labels

    assert len(np.unique(train_labels)) == NUM_LABELS

    return True

@ip.util.unit_test
def test_multilayer_perceptron():
    import imagepypelines as ip

    resizer = ip.Resizer(32,32) #28x28
    features = ip.PretrainedNetwork() # generate features
    pca = ip.PCA(256)
    classifier = ip.MultilayerPerceptron(neurons=512,
                                            validation=.1,
                                            num_hidden=3,
                                            dropout=.35,
                                            learning_rate=.01) # NN classifier
    # there are a lot more parameters you can tweak!

    pipeline = ip.Pipeline([resizer,features,pca,classifier])
    pipeline.rename('test_multilayer_perceptron')
    pipeline.debug()

    # for this example, we'll need to load the standard Mnist handwriting dataset
    # built into `imagepypelines`
    mnist = ip.Mnist()
    train_data, train_labels = mnist.get_train()
    test_data, ground_truth = mnist.get_test()

    # train the classifier
    pipeline.train(train_data,train_labels)

    # test the classifier
    predictions = pipeline.process(test_data)

    # print the accuracy
    accuracy = ip.accuracy(predictions,ground_truth)
    print('accuracy is ', accuracy)

    if len(predictions) == len(test_data):
        return True
    return False


@ip.util.unit_test
def test_linear_svm():
    import imagepypelines as ip

    resizer = ip.Resizer(32,32) #28x28
    features = ip.PretrainedNetwork() # generate features
    pca = ip.PCA(256)
    classifier = ip.LinearSvm()

    pipeline = ip.Pipeline([resizer,features,pca,classifier])
    pipeline.rename('test_linear_svm')
    pipeline.debug()

    # for this example, we'll need to load the standard Mnist handwriting dataset
    # built into `imagepypelines`
    mnist = ip.Mnist()
    train_data, train_labels = mnist.get_train()
    test_data, ground_truth = mnist.get_test()

    # train the classifier
    pipeline.train(train_data,train_labels)

    # test the classifier
    predictions = pipeline.process(test_data)

    # print the accuracy
    accuracy = ip.accuracy(predictions,ground_truth)
    print('accuracy is ', accuracy)

    if len(predictions) == len(test_data):
        return True
    return False


@ip.util.unit_test
def test_rbf_svm():
    import imagepypelines as ip

    resizer = ip.Resizer(32,32) #28x28
    features = ip.PretrainedNetwork() # generate features
    pca = ip.PCA(256)
    classifier = ip.RbfSvm()

    pipeline = ip.Pipeline([resizer,features,pca,classifier])
    pipeline.rename('test_rbf_svm')
    pipeline.debug()

    # for this example, we'll need to load the standard Mnist handwriting dataset
    # built into `imagepypelines`
    mnist = ip.Mnist()
    train_data, train_labels = mnist.get_train()
    test_data, ground_truth = mnist.get_test()

    # train the classifier
    pipeline.train(train_data,train_labels)

    # test the classifier
    predictions = pipeline.process(test_data)

    # print the accuracy
    accuracy = ip.accuracy(predictions,ground_truth)
    print('accuracy is ', accuracy)

    if len(predictions) == len(test_data):
        return True
    return False


@ip.util.unit_test
def test_poly_svm():
    import imagepypelines as ip

    resizer = ip.Resizer(32,32) #28x28
    features = ip.PretrainedNetwork() # generate features
    pca = ip.PCA(256)
    classifier = ip.PolySvm()

    pipeline = ip.Pipeline([resizer,features,pca,classifier])
    pipeline.rename('test_poly_svm')
    pipeline.debug()

    # for this example, we'll need to load the standard Mnist handwriting dataset
    # built into `imagepypelines`
    mnist = ip.Mnist()
    train_data, train_labels = mnist.get_train()
    test_data, ground_truth = mnist.get_test()

    # train the classifier
    pipeline.train(train_data,train_labels)

    # test the classifier
    predictions = pipeline.process(test_data)

    # print the accuracy
    accuracy = ip.accuracy(predictions,ground_truth)
    print('accuracy is ', accuracy)

    if len(predictions) == len(test_data):
        return True
    return False

@ip.util.unit_test
def test_sigmoid_svm():
    import imagepypelines as ip

    resizer = ip.Resizer(32,32) #28x28
    features = ip.PretrainedNetwork() # generate features
    pca = ip.PCA(256)
    classifier = ip.SigmoidSvm()

    pipeline = ip.Pipeline([resizer,features,pca,classifier])
    pipeline.rename('test_sigmoid_svm')
    pipeline.debug()

    # for this example, we'll need to load the standard Mnist handwriting dataset
    # built into `imagepypelines`
    mnist = ip.Mnist()
    train_data, train_labels = mnist.get_train()
    test_data, ground_truth = mnist.get_test()

    # train the classifier
    pipeline.train(train_data,train_labels)

    # test the classifier
    predictions = pipeline.process(test_data)

    # print the accuracy
    accuracy = ip.accuracy(predictions,ground_truth)
    print('accuracy is ', accuracy)

    if len(predictions) == len(test_data):
        return True
    return False






@ip.util.unit_test
def test_all_pretrained_networks():
    import imagepypelines as ip
    import cv2

    filenames = ip.standard_image_filenames()
    images = [cv2.imread(f,cv2.IMREAD_COLOR) for f in filenames]
    printer = ip.get_printer('test_all_pretrained_networks')

    success = []
    for i,network_name in enumerate(ip.PRETRAINED_NETWORKS):
        try:
            printer.info("testing {}...".format(network_name))
            resizer = ip.Resizer(80,80)
            pretrained = ip.PretrainedNetwork(network_name)

            pipeline = ip.Pipeline([resizer,pretrained])
            pipeline.process(images)

            del pretrained
            del pipeline
            success.append(True)
            printer.info("{}/{} test successful!"\
                            .format(i+1,len(ip.PRETRAINED_NETWORKS)))


        except Exception as e:
            printer.error("failure processing ",network_name)
            success.append(False)

    return all(success)


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
