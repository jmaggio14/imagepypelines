#
# @Email:  jmaggio14@gmail.com
#
# MIT License: https://github.com/jmaggio14/imsciutils/blob/master/LICENSE
#
# Copyright (c) 2018 Jeff Maggio, Nathan Dileas, Ryan Hartzell
#
import os
import glob
import random
import itertools
from collections import deque

import imsciutils as iu
from .. import core

@core.experimental()
class DatasetManager(object):
    def __init__(self,input_dir,k_folds,extensions=None,recursive=False,random_seed=None):
        # building printer and checking instantation args
        self.printer = core.get_printer(self.__class__.__name__)

        if extensions is None:
            extensions = ['']
        self.__error_check(input_dir, k_folds, extensions, recursive, random_seed)

        self.input_dir = input_dir
        self.k_folds = int(k_folds)
        self.extensions = extensions
        self.recursive = recursive

        self.data_filenames = self.make_data_lists()
        self.fold_index = 1

    def __error_check(self, input_dir, k_folds, extensions, recursive, random_seed):
        """
        performs error checking on the instantation args for this class
        """
        # checking to make sure the input directory exists
        if not os.path.exist(input_dir):
            error_msg = "Unable to find input_dir '{}'".format(input_dir)
            self.printer.error(error_msg)
            raise FileNotFoundError(error_msg)

        # making sure k_folds is an integer greater than one
        if not isinstance(k_folds,(int,float)):
            error_msg = "'k_folds' must be an int"
            self.printer.error(error_msg)
            raise TypeError(error_msg)
        # checking that k_folds is 2 or greater
        elif not k_folds > 1:
            error_msg = "'k_folds' must be 2 or greater"
            self.printer.error(error_msg)
            raise ValueError(error_msg)
        # checking to make sure 'extensions' is a tuple or list of acceptable image extensions
        if not isinstance(extensions,(tuple,list)):
            error_msg = "'extensions' must be a tuple or list of acceptable image extensions, or None for all"
            self.printer.error(error_msg)
            raise TypeError(error_msg)
        # making sure every extension is a string
        elif not all( isinstance(ext,str) for ext in extensions ):
            error_msg = "all image extensions must be strings"
            self.printer.error(error_msg)
            raise TypeError(error_msg)

        # checking that random seed is of the correct type
        if not isinstance(random_seed,(int,float,type(None))):
            error_msg = "random_seed must be a int, float or Nonetype"
            self.printer.error(error_msg)
            raise TypeError(error_msg)

    def __str__(self):
        return "DatasetManager ({}/{} folds)".format(self.fold_index,self.k_folds)

    def __repr__(self):
        return str(self) + " - input_dir: {}".format(self.input_dir)

    def make_data_lists(self):
        """
        generates a list of data_filenames
        """
        if self.recursive:
            join_args = (self.input_dir,'**')
        else:
            join_args = (self.input_dir,)

        data_filenames = []
        for ext in extensions:
            glob_string = os.path.join(*join_args,'*' + ext)
            data_filenames.extend( glob.glob(glob_string) )

        # shuffling the data in place before chunking
        random.seed(self.random_seed)
        random.shuffle(data_filenames)

        # chunking the data into k chunks for k_fold cross_validation
        it = iter(data_filenames)
        data_filenames = deque( iter(lambda: tuple(itertools.islice(it, self.k_folds)), ()) )

        return data_filenames


    def get_train_test(self):
        """
        returns train and test data filenames in the form of a list
        """
        # getting datafilename list because deques are not sliceable
        data_list = list(self.data_filenames)

        train_data = list( chain( *data_list[:self.k_folds-1] ) )
        test_data = data_list[-1]

        return train_data, test_data

    def rotate(self):
        self.data_filenames.rotate()
        self.fold_index += 1

        # printing fold warnings / updates to the terminal
        if self.fold_index > self.k_folds:
            warning_msg = "WARNING! on fold {}, this dataset was only made for {} folds, which means you are seeing data for fold {}"
            warning_msg = warning_msg.format(self.fold_index,self.k_folds, (self.k_folds % self.fold_index + 1))
            self.printer.warning(warning_msg)
        else:
            info_msg = "ready for fold {}/{}".format(self.fold_index,self.k_folds)
            self.printer.info(info_msg)

    @property
    def fold(self):
        return self.fold_index
