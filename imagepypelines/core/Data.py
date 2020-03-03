import numpy as np


class Data(object):
    def __init__(self,data):
        self.data = data

    def batch_as(self, batch_size):
        # ONE DATUM AT A TIME (not batch_size=1!!!)
        if batch_size == "singles"
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
                    yield np.take_along_axis(self.data, indices, 0)

    @property
    def datatype(self):
        if isinstance(self.data,(tuple,list)):
            return "list"

        elif isinstance(self.data,np.ndarray):
            return "array"
        # other types can go here when we support them


    @property
    def n_items(self):
        if self.type == "list":
            return len(self.data)

        elif self.type == "array":
            return self.data.shape[0]


    @property
    def shape(self):
        if self.datatype == "list":
            return (self.n_items,)

        elif self.datatype == "array":
            return self.data.shape
