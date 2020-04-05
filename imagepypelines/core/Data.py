# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018-2020 Jeff Maggio, Ryan Hartzell, and collaborators
#
import numpy as np


class Data(object):
    """Object to batch lists or arrays as block processable data

    Attributes:
        data (any type): the raw data
    """
    def __init__(self, data):
        """instantiates the Data object

        Args:
            data (any type): the raw data
        """
        self.data = data

    ############################################################################
    def n_batches_with(self, batch_type):
        """calculates the number of batches generated with the given batch_type"""
        if batch_type == "each":
            return self.n_items
        elif batch_type == "all":
            return 1

    ############################################################################
    def as_all(self):
        """returns all the data in it's raw form"""
        return self.data

    ############################################################################
    def as_each(self):
        """returns a generator the returns each datum individually"""
        for d in self.data:
            yield d

    ############################################################################
    def pop(self):
        """returns the data, and then removes it from this object"""
        data = self.data
        self.data = None
        return data

    ############################################################################
    def grab(self):
        """returns the data in it's raw form"""
        return self.data

    ############################################################################
    def __len__(self):
        return len(self.data)

    ############################################################################
    #                               properties
    ############################################################################
    @property
    def n_items(self):
        """int: number of items loaded into the pipeline"""
        return len(self)

    ############################################################################
    @property
    def shape(self):
        """tuple: the shape of the data"""
        if self.datatype == "list":
            return (self.n_items,)

        elif self.datatype == "array":
            return self.data.shape
