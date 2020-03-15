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
    def n_batches_with(self, batch_size):
        """calculates the number of batches generated with the given batch_size"""
        if batch_size == "singles":
            return self.n_items
        elif batch_size == "all":
            return 1
        else:
            return int(ceil(float(self.n_items) / batch_size))

    ############################################################################
    def batch_as(self, batch_size):
        """returns a generator that generates data batches of given batch_size"""
        # ONE DATUM AT A TIME (not batch_size=1!!!)
        if batch_size == "singles":
            # LIST
            for datum in self.data:
                yield datum

        # ALL DATA AT ONCE
        elif batch_size == "all":
            # no need to differentiate between different types here
            yield self.data

        # SLICING INTO DISCRETE BATCH SIZE
        elif isinstance(batch_size, int):
            n_items = self.n_items
            for start in range(0, n_items, batch_size):
                end = min(n_items, start+batch_size)
                yield self.data[start:end]

    ############################################################################
    def pop(self):
        """returns the data, and then removes it from this object"""
        data = self.data
        self.data = None
        return data

    ############################################################################
    def __len__(self):
        return self.n_items

    ############################################################################
    #                               properties
    ############################################################################
    @property
    def n_items(self):
        """int: number of items loaded into the pipeline"""
        return len(self.data)
