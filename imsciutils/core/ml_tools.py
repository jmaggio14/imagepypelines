#
# @Email:  jmaggio14@gmail.com
#
# MIT License: https://github.com/jmaggio14/imsciutils/blob/master/LICENSE
#
# Copyright (c) 2018 Jeff Maggio, Nathan Dileas, Ryan Hartzell
#
import numpy as np
from itertools import islice, chain

def accuracy(predicted,ground_truth):
    """calculates accuracy given ground truth and predicted labels"""
    num_correct = np.sum(np.asarray(predicted) == np.asarray(ground_truth))
    return float(num_correct) / len(predicted)


def batch(data_list, batch_size):
    """chunks a list into multiple batch_size chunks, the last batch will
    be truncated if the data_list length isn't a multiple of batch_size
    """
    data_list = iter(data_list)
    return list(iter( lambda: list(islice(data_list, size)), ()) )

def batches_to_list(batches):
    """turns nested iterables into a single list"""
    return list( chain(*batches) )
