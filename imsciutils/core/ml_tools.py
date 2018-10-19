#
# @Email:  jmaggio14@gmail.com
#
# MIT License: https://github.com/jmaggio14/imsciutils/blob/master/LICENSE
#
# Copyright (c) 2018 Jeff Maggio, Nathan Dileas, Ryan Hartzell
#
import numpy as np

def accuracy(predicted,ground_truth):
    num_correct = np.sum(np.asarray(predicted) == np.asarray(ground_truth))
    return float(num_correct) / len(predicted)
