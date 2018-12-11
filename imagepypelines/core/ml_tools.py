# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018 Jeff Maggio, Nathan Dileas, Ryan Hartzell
import numpy as np
from itertools import islice, chain
import scipy.stats
import random

def accuracy(predicted,ground_truth):
    """calculates accuracy given ground truth and predicted labels"""
    num_correct = np.sum(np.asarray(predicted) == np.asarray(ground_truth))
    return float(num_correct) / len(predicted)

def confidence_99(data):
    """returns the 99% confidence mean and deviation for the given
        distribution

    Args:
        data(array-like): data to find the confidence interval for,
            in machine learning applications, this is usually accuracy
            for K-fold cross validation

    Returns:
        float: the mean for this distributions
        float: +/- deviation for this confidence interval

    Example:
        >>> # get 99% confidence interval
        >>> mean, deviation = confidence_99(accuracies)
    """
    return confidence(data,.99)

def confidence_95(data):
    """returns the 95% confidence mean and deviation for the given
        distribution

    Args:
        data(array-like): data to find the confidence interval for,
            in machine learning applications, this is usually accuracy
            for K-fold cross validation

    Returns:
        float: the mean for this distributions
        float: +/- deviation for this confidence interval

    Example:
        >>> # get 95% confidence interval
        >>> mean, deviation = confidence_95(accuracies)
    """
    return confidence(data,.95)

def confidence_90(data):
    """returns the 90% confidence mean and deviation for the given
        distribution

    Args:
        data(array-like): data to find the confidence interval for,
            in machine learning applications, this is usually accuracy
            for K-fold cross validation

    Returns:
        float: the mean for this distributions
        float: +/- deviation for this confidence interval

    Example:
        >>> # get 90% confidence interval
        >>> mean, deviation = confidence_90(accuracies)
    """
    return confidence(data,.90)


def confidence(data, confidence=0.95):
    """returns the confidence mean and deviation for the given
        confidence interval

    Args:
        data(array-like): data to find the confidence interval for,
            in machine learning applications, this is usually accuracy
            for K-fold cross validation
        confidence(float): confidence interval between 0-1, to find
            the desired mean and deviation for

    Returns:
        float: the mean for this distributions
        float: +/- deviation for this confidence interval

    Example:
        >>> # get 95% confidence interval
        >>> mean, deviation = confidence(accuracies,.95)
    """
    data = np.asarray(data,dtype=np.float32)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * scipy.stats.t.ppf((1 + confidence) / 2.0, len(data)-1)
    return m, h



def batch(data_list, batch_size):
    """chunks a list into multiple batch_size chunks, the last batch will
    be truncated if the data_list length isn't a multiple of batch_size
    """
    data_list = iter(data_list)
    return list(iter( lambda: list(islice(data_list, batch_size)), ()) )

def batches_to_list(batches):
    """turns nested iterables into a single list"""
    return list( chain(*batches) )


def sample(data,labels,sample_fraction=.05):
    """function to randomly select data and corresponding labels using a uniform
    distribution

    Example:
        >>> import random
        >>> random.seed(0)
        >>> import imagepypelines as ip
        >>> data = [0,1,2,3,4,5,6,7,8,9]
        >>> labels = ['0','1','2','3','4','5','6','7','8','9']
        >>>
        >>> small_data, small_labels = ip.sample(data,labels,.2)
        >>> small_data
        [6, 9]
        >>> small_labels
        ['6', '9']

    """
    assert len(data) == len(labels), \
        "you must have an equal number of data and labels"

    combined = list( zip(data, labels) )
    n = int(sample_fraction * len(data))
    sampled = random.sample(combined,n)
    sampled_data, sampled_labels = zip(*sampled)
    return list(sampled_data), list(sampled_labels)
