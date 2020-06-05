# # @Email: jmaggio14@gmail.com
# # @Website: https://www.imagepypelines.org/
# # @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# # @github: https://github.com/jmaggio14/imagepypelines
# #
# # Copyright (c) 2018 - 2020 Jeff Maggio, Jai Mehra, Ryan Hartzell
# import numpy as np
# from itertools import islice, chain, product
# import scipy.stats
# import random
# import math
# import importlib
# import collections
#
#
# ################################################################################
# #                                  Functions
# ################################################################################
#
# def accuracy(predicted,ground_truth):
#     """calculates accuracy given ground truth and predicted labels"""
#     num_correct = np.sum(np.asarray(predicted) == np.asarray(ground_truth))
#     return float(num_correct) / len(predicted)
#
# def confidence_99(data):
#     """returns the 99% confidence mean and deviation for the given
#         distribution
#
#     Args:
#         data(array-like): data to find the confidence interval for,
#             in machine learning applications, this is usually accuracy
#             for K-fold cross validation
#
#     Returns:
#         float: the mean for this distributions
#         float: +/- deviation for this confidence interval
#
#     Example:
#         >>> import numpy as np
#         >>> import imagepypelines as ip
#         >>> # create sample test 'accuracies' from a normal distribution
#         >>> # mean accuracy is 75%, std is 10% for this example
#         >>> accuracies = np.random.normal(.75, .1, 1000)
#         >>> # get 99% confidence interval
#         >>> mean, error = ip.confidence_99(accuracies)
#     """
#     return confidence(data,.99)
#
# def confidence_95(data):
#     """returns the 95% confidence mean and deviation for the given
#         distribution
#
#     Args:
#         data(array-like): data to find the confidence interval for,
#             in machine learning applications, this is usually accuracy
#             for K-fold cross validation
#
#     Returns:
#         float: the mean for this distributions
#         float: +/- deviation for this confidence interval
#
#     Example:
#         >>> import numpy as np
#         >>> import imagepypelines as ip
#         >>> # create sample test 'accuracies' from a normal distribution
#         >>> # mean accuracy is 75%, std is 10% for this example
#         >>> accuracies = np.random.normal(.75, .1, 1000)
#         >>> # get 95% confidence interval
#         >>> mean, error = ip.confidence_95(accuracies)
#     """
#     return confidence(data,.95)
#
# def confidence_90(data):
#     """returns the 90% confidence mean and deviation for the given
#         distribution
#
#     Args:
#         data(array-like): data to find the confidence interval for,
#             in machine learning applications, this is usually accuracy
#             for K-fold cross validation
#
#     Returns:
#         float: the mean for this distributions
#         float: +/- deviation for this confidence interval
#
#     Example:
#         >>> import numpy as np
#         >>> import imagepypelines as ip
#         >>> # create sample test 'accuracies' from a normal distribution
#         >>> # mean accuracy is 75%, std is 10% for this example
#         >>> accuracies = np.random.normal(.75, .1, 1000)
#         >>> # get 90% confidence interval
#         >>> mean, error = ip.confidence_90(accuracies)
#     """
#     return confidence(data,.90)
#
#
# def confidence(data, confidence=0.95):
#     """returns the confidence mean and deviation for the given
#         confidence interval
#
#     Args:
#         data(array-like): data to find the confidence interval for,
#             in machine learning applications, this is usually accuracy
#             for K-fold cross validation
#         confidence(float): confidence interval between 0-1, to find
#             the desired mean and deviation for
#
#     Returns:
#         float: the mean for this distributions
#         float: +/- deviation for this confidence interval
#
#     Example:
#         >>> import numpy as np
#         >>> import imagepypelines as ip
#         >>> # create sample test 'accuracies' from a normal distribution
#         >>> # mean accuracy is 75%, std is 10% for this example
#         >>> accuracies = np.random.normal(.75, .1, 1000)
#         >>> # get 95% confidence interval
#         >>> mean, error = ip.confidence(accuracies,.95)
#     """
#     data = np.asarray(data,dtype=np.float32)
#     # calculate mean and standard error of measurement
#     m, se = np.mean(data), scipy.stats.sem(data)
#     # find error using the percent point function and standard error
#     h = se * scipy.stats.t.ppf((1 + confidence) / 2.0, len(data)-1)
#     return m, h
#
#
# def chunk(data,n):
#     """chunk a list into n chunks"""
#     chunk_size = math.ceil( len(data) / n )
#     return batch(data, chunk_size)
#
# def batch(data, batch_size):
#     """chunks a list into multiple batch_size chunks, the last batch will
#     be truncated if the data length isn't a multiple of batch_size
#     """
#     data = iter(data)
#     return list(iter( lambda: list(islice(data, batch_size)), []) )
#
# def chunks2list(batches):
#     """turns nested iterables into a single list"""
#     return list( chain(*batches) )
#
# def xsample(data,sample_fraction):
#     """function to randomly sample list data using a uniform distribution
#     """
#     assert isinstance(data,list),"data must be a list"
#     assert sample_fraction >= 0 and sample_fraction <= 1,\
#         "sample_fraction must be a float between 0 and 1"
#
#     n = int(sample_fraction * len(data))
#     sampled = random.sample(data,n)
#     return sampled
#
# def xysample(data,labels,sample_fraction=.05):
#     """function to randomly sample list data and corresponding labels using a uniform
#     distribution
#
#     Example:
#         >>> import random
#         >>> random.seed(0)
#         >>> import imagepypelines as ip
#         >>> data = [0,1,2,3,4,5,6,7,8,9]
#         >>> labels = ['0','1','2','3','4','5','6','7','8','9']
#         >>>
#         >>> small_data, small_labels = ip.xysample(data,labels,.2)
#     """
#     assert isinstance(data,list),"data must be a list"
#     assert isinstance(labels,list),"labels must be a list"
#     assert len(data) == len(labels), \
#         "you must have an equal number of data and labels"
#     assert min(0,sample_fraction) == 0 and max(1,sample_fraction) == 1,\
#         "sample_fraction must be a float between 0 and 1"
#
#     combined = list( zip(data, labels) )
#     n = int(sample_fraction * len(data))
#     sampled = random.sample(combined,n)
#     sampled_data, sampled_labels = zip(*sampled)
#     return list(sampled_data), list(sampled_labels)
#
#
#
# ################################################################################
# #                                  CLASSES
# ################################################################################
# class ConfigFactory(object):
#     """
#     argument Permuter object for generating permutations of function arguments
#     or configurations for config files
#
#     For example, in many machine learning applications, parameters have to
#     be tweaked frequently to optimize a model. This can be a tedious task
#     and frequently involves a human tweaking configurations files. This
#     object is meant to simplify that process by generating permutations
#     from a sample of arguments and keyword arguments
#
#     Example:
#         >>> import imagepypelines as ip
#         >>> def run_important_test(arg1,arg2,arg3,first,second,third):
#         ...    # real code will do something
#         ...    pass
#         >>> arg_trials = [
#         ...        [1,2,3], # trials for first positional argument
#         ...        ['a','b','c'], # trials for second positional arguments
#         ...        ['y','z'], # trials for third positional argument
#         ...        ]
#         >>> kwarg_trials = {
#         ...            'first':None, # trials for 'first' keyword argument
#         ...            'second':['I','J','K'], # trials for 'second' keyword argument
#         ...            'third':['i','j','k'], # trials for 'third' keyword argument
#         ...            }
#
#         >>> permuter = ip.ConfigFactory(*arg_trials,**kwarg_trials)
#         >>> for args,kwargs in permuter:
#         ...    run_important_test(*args,**kwargs)
#     """
#     def __init__(self,*arg_trials,**kwarg_trials):
#         arg_list = []
#         self.num_positional = len(arg_trials)
#
#         # making positional arguments iterable if they aren't already
#         for arg in arg_trials:
#             if not isinstance(arg,collections.Iterable):
#                 arg = [arg]
#             arg_list.append(arg)
#
#         # making keyword arguments iterable if they aren't already
#         for key,val in kwarg_trials.items():
#             if not isinstance(val,collections.Iterable):
#                 kwarg_trials[key] = [val]
#
#         self.kwarg_keys = sorted( kwarg_trials.keys() )
#         kwarg_vals = [kwarg_trials[k] for k in self.kwarg_keys]
#
#         # storing all arguments in a list
#         all_args = arg_list + kwarg_vals
#         self.num_permutations = int( np.prod([ len(args) for args in all_args ] ) )
#         self._remaining = self.num_permutations
#
#         # generation of permutations using a cartesian product
#         self.permutations = product(*all_args)
#
#     def __iter__(self):
#         """
#         iterates through the permutations
#         """
#         self._remaining = self.num_permutations
#         #retrieving all permutations as a generator
#         for perm in self.permutations:
#             args = perm[:self.num_positional]
#             kwargs = dict( zip(self.kwarg_keys,perm[self.num_positional:]) )
#             yield args,kwargs
#             self._remaining -= 1
#
#     def __len__(self):
#         """returns the number of total permutations"""
#         return self.num_permutations
#
#     def remaining(self):
#         """returns the number of remaining permutations"""
#         return self._remaining
#
#     def __str__(self):
#         num_remaining = "unknown"
#         if hasattr(self,'_remaining'):
#             num_remaining = self.remaining()
#         out = "ConfigFactory ({} permutations remaining)".format(num_remaining)
#         return out
#
#     def __repr__(self):
#         return str(self) + ' @{}'.format( hex(id(self)) )
#
#
# class DatasetRetrieval(object):
#     """Retrieves a pipeline compatible dataset"""
#     def __init__(self, dataset, fraction=1):
#         data = importlib.import_module('keras.datasets.' + dataset)
#         from keras import backend as K
#         K.set_image_data_format('channels_last')
#
#         (x_train,y_train), (x_test,y_test) = data.load_data()
#
#         GRAY = True if x_train.ndim == 3 else False
#
#         if GRAY:
#             self.x_train = [np.squeeze(x_train[i,:,:]) for i in range(x_train.shape[0])]
#             self.y_train = [int(i) for i in y_train]
#
#             self.x_test = [np.squeeze(x_test[i,:,:]) for i in range(x_test.shape[0])]
#             self.y_test = [int(i) for i in y_test]
#         else:
#             self.x_train = [np.squeeze(x_train[i,:,:,:]) for i in range(x_train.shape[0])]
#             self.y_train = [int(i) for i in y_train]
#
#             self.x_test = [np.squeeze(x_test[i,:,:,:]) for i in range(x_test.shape[0])]
#             self.y_test = [int(i) for i in y_test]
#
#         self.fraction = fraction
#
#         self.x_train, self.y_train = xysample(self.x_train,
#                                                 self.y_train,
#                                                 self.fraction)
#         self.x_test, self.y_test = xysample(self.x_test,
#                                                 self.y_test,
#                                                 self.fraction)
#
#     def get_sorted_train(self):
#         """retrieves data and labels for train set sorted by label"""
#
#         indexes = list(range( len(self.y_train) ))
#         indexes.sort(key=self.y_train.__getitem__)
#         sorted_data = list( map(self.x_train.__getitem__, indexes) )
#         sorted_labels = list( map(self.y_train.__getitem__, indexes) )
#
#         return sorted_data,sorted_labels
#
#     def get_sorted_test(self):
#         """retrieves data and labels for test set sorted by label"""
#
#         indexes = list(range( len(self.y_test) ))
#         indexes.sort(key=self.y_test.__getitem__)
#         sorted_data = list( map(self.x_test.__getitem__, indexes) )
#         sorted_labels = list( map(self.y_test.__getitem__, indexes) )
#
#         return sorted_data,sorted_labels
#
#     def get_train(self):
#         """
#         retrieves the mnist numbers train dataset using keras
#
#         Args:
#             None
#         Returns:
#             list: training data
#             list: training labels
#         """
#         return self.x_train, self.y_train
#
#     def get_test(self):
#         """
#         retrieves the mnist numbers test dataset using keras
#
#         Args:
#             None
#         Returns:
#             list: testing data
#             list: testing labels
#         """
#         return self.x_test, self.y_test
#
#
# class Mnist(DatasetRetrieval):
#     """
#     Object to load the MNIST numbers dataset in a pipeline compatible format
#
#     Attributes:
#         x_train(list): 60,000 monochromatic 28x28 images
#         y_train(list): corresponding integer labels for the data
#         x_test(list): 10,000 monochromatic 28x28 images
#         y_test(list): corresponding integer labels for the data
#     """
#     def __init__(self, fraction=1):
#         super().__init__('mnist', fraction)
#
#     def get_train(self):
#         """
#         retrieves the mnist numbers train dataset using keras
#
#         Args:
#             None
#         Returns:
#             x_train(list): 60,000 monochromatic 28x28 images
#             y_train(list): corresponding integer labels for the data
#         """
#         return super().get_train()
#
#     def get_test(self):
#         """
#         retrieves the mnist numbers test dataset using keras
#
#         Args:
#             None
#         Returns:
#             x_test(list): 10,000 monochromatic 28x28 images
#             y_test(list): corresponding integer labels for the data
#         """
#         return super().get_test()
#
#
# class MnistFashion(DatasetRetrieval):
#     """
#     Object to load the MNIST fashion dataset in a pipeline compatible format
#
#     Attributes:
#         x_train(list): 60,000 monochromatic 28x28 images
#         y_train(list): corresponding integer labels for the data
#         x_test(list): 10,000 monochromatic 28x28 images
#         y_test(list): corresponding integer labels for the data
#     """
#     def __init__(self, fraction=1):
#         super().__init__('fashion_mnist', fraction)
#
#     def get_train(self):
#         """
#         retrieves the mnist numbers train dataset using keras
#
#         Args:
#             None
#         Returns:
#             x_train(list): 60,000 monochromatic 28x28 images
#             y_train(list): corresponding integer labels for the data
#         """
#         return super().get_train()
#
#     def get_test(self):
#         """
#         retrieves the mnist numbers test dataset using keras
#
#         Args:
#             None
#         Returns:
#             x_test(list): 10,000 monochromatic 28x28 images
#             y_test(list): corresponding integer labels for the data
#         """
#         return super().get_test()
#
#
# class Cifar10(DatasetRetrieval):
#     """
#     Object to load the cifar10 dataset in a pipeline compatible format
#
#     Attributes:
#         x_train(list): 50,000 color 32,32,3 images
#         y_train(list): corresponding integer labels for the data
#         x_test(list): 10,000 color 32,32,3 images
#         y_test(list): corresponding integer labels for the data
#
#     """
#     def __init__(self, fraction=1):
#         super().__init__('cifar10', fraction)
#
#     def get_train(self):
#         """
#         retrieves the cifar 10 labels train dataset using keras
#
#         Args:
#             None
#         Returns:
#             x_train(list): 50,000 color 32,32,3 images
#             y_train(list): corresponding integer labels for the data
#         """
#         return self.x_train,self.y_train
#
#     def get_test(self):
#         """
#         retrieves the cifar 10 labels test dataset using keras
#
#         Args:
#             None
#         Returns:
#             x_test(list): 10,000 color 32,32,3 images
#             y_test(list): corresponding integer labels for the data
#         """
#         return self.x_test,self.y_test
#
#
# class Cifar100(DatasetRetrieval):
#     """
#     Object to load the cifar100 dataset in a pipeline compatible format
#
#     Args:
#         label_mode(string): 'fine' for individual labels (100 unique),
#             'coarse' for superclass labels (20 unique)
#
#     Attributes:
#         x_train(list): 50,000 color 32,32,3 images
#         y_train(list): corresponding integer labels for the data
#         x_test(list): 10,000 color 32,32,3 images
#         y_test(list): corresponding integer labels for the data
#
#     """
#     def __init__(self, fraction=1):
#         super().__init__('cifar100', fraction)
#
#     def get_train(self):
#         """
#         retrieves the cifar 100 labels train dataset using keras
#
#         Args:
#             None
#         Returns:
#             x_train(list): 50,000 color 32,32,3 images
#             y_train(list): corresponding integer labels for the data
#         """
#         return self.x_train,self.y_train
#
#     def get_test(self):
#         """
#         retrieves the cifar 100 labels test dataset using keras
#
#         Args:
#             None
#         Returns:
#             x_test(list): 10,000 color 32,32,3 images
#             y_test(list): corresponding integer labels for the data
#         """
#         return self.x_test,self.y_test
