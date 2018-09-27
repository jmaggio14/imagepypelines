#
# @Email:  jmaggio14@gmail.com
#
# MIT License: https://github.com/jmaggio14/imsciutils/blob/master/LICENSE
#
# Copyright (c) 2018 Jeff Maggio, Nathan Dileas, Ryan Hartzell
#
import numpy as np

def get_mnist():
    """
    retrieves the mnist dataset using keras

    Args:
        None

    Returns:
        data (tuple): (train_data,train_label), (test_data,test_labels)

    """
    from keras.datasets import mnist
    return mnist.load_data()

def get_fashion_mnist():
    """
    retrieves the fashion_mnist dataset using keras

    Args:
        None

    Returns:
        data (tuple): (train_data,train_label), (test_data,test_labels)

    """
    from keras.datasets import fashion_mnist
    return fashion_mnist.load_data()


def get_cifar10():
    """
    retrieves the cifar10 dataset using keras

    Args:
        None

    Returns:
        data (tuple): (train_data,train_label), (test_data,test_labels)

    """
    from keras.datasets import cifar10
    return cifar10.load_data()

def get_cifar100(fine=True):
    """
    retrieves the cifar100 dataset using keras

    Args:
        None

    Returns:
        data (tuple): (train_data,train_label), (test_data,test_labels)

    """
    from keras.datasets import cifar100
    if fine:
        label_mode = 'fine'
    else:
        label_mode = 'coarse'
    return cifar100.load_data()


def dataset_to_list(arr):
    return np.vsplit(arr, arr.shape[0])
