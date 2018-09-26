#
# @Email:  jmaggio14@gmail.com
#
# MIT License
#
# Copyright (c) 2018 Jeff Maggio, Nathan Dileas, Ryan Hartzell
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
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
