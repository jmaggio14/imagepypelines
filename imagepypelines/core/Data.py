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
        if batch_size == "each":
            return self.n_items
        elif batch_size == "all":
            return 1
        else:
            return int(ceil(float(self.n_items) / batch_size))

    ############################################################################
    def batch_as(self, batch_size):
        """returns a generator that generates data batches of given batch_size"""
        # ONE DATUM AT A TIME (not batch_size=1!!!)
        if batch_size == "each":
            # LIST
            # return every element if data is a list
            if self.datatype == "list":
                for d in self.data:
                    yield d

            # ARRAY
            # return every row if it's an array (first axis)
            elif self.datatype == "array":
                for row in self.data:
                    yield d

        # ALL DATA AT ONCE
        elif batch_size == "all":
            # no need to differentiate between different types here
            yield self.data


        # DISCRETE BATCH SIZE
        elif isinstance(batch_size, int):
            n_items = self.n_items

            # DATA
            if self.datatype == "list":
                for start in range(0, n_items, batch_size):
                    end = min(n_items, start+batch_size)
                    yield self.data[start:end]
            # ARRAY
            elif self.datatype == "array":
                for start in range(0, n_items, batch_size):
                    end = min(n_items, start+batch_size)
                    indices = np.arange(start, end)
                    # NOTE: check if this results in correct ndim
                    yield self.data[start:end,...]

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
    def datatype(self):
        """str: the type of data loaded"""
        if isinstance(self.data,(tuple,list)):
            return "list"

        elif isinstance(self.data,np.ndarray):
            return "array"
        # other types can go here when we support them

        else:
            raise RuntimeError("invalid datatype ('%s')" % type(self.data))

    ############################################################################
    @property
    def n_items(self):
        """int: number of items loaded into the pipeline"""
        if self.datatype == "list":
            return len(self.data)

        elif self.datatype == "array":
            return self.data.shape[0]

    ############################################################################
    @property
    def shape(self):
        """tuple: the shape of the data"""
        if self.datatype == "list":
            return (self.n_items,)

        elif self.datatype == "array":
            return self.data.shape
