import numpy as np
from .Exceptions import ArgTypeError

# --------------------------------------------------------------
# make sure all inputs are in valid containers so the Data
# object can work with them
# (this typically means that all data passed in are in lists or numpy
# array - but anything with __len__, __getitem__, and __getslice__)
# will work
# --------------------------------------------------------------
# check positional input containers for validity
# for i,d in enumerate(pos_data):
#     if not self._is_valid_container(d):
#         # log the output and raise an error
#         msg = INVALID_CONTAINER_MSG.format(
#                                             input_name=self.args[i],
#                                             con_methods=REQUIRED_CONTAINER_ATTRIBUTES
#                                             )
#         self.logger.error(msg)
#         raise PipelineError(msg)
#
# # check keyword input containers for validity
# for k,d in kwdata.items():
#     if not self._is_valid_container(d):
#         # log the output and raise an error
#         msg = INVALID_CONTAINER_MSG.format(
#                                             input_name=k,
#                                             con_methods=REQUIRED_CONTAINER_ATTRIBUTES
#                                             )
#         self.logger.error(msg)
#         raise PipelineError(msg)

# CONTAINERS MUST HAVE THE FOLLOWING
REQUIRED_CONTAINER_ATTRIBUTES = [
                                '__len__',
                                '__getitem__',
                                '__getslice__'
                                ]
"""methods that every Input data object in the Pipeline must have"""


INVALID_CONTAINER_MSG = "Invalid Container object for Input '{input_name}' - "\
            + "Pipeline Inputs must contain the methods: {con_methods}. " \
            + "(this usually means your input data isn't a numpy array, list, "\
            + "or tuple)"
"""Error message raised if there is an inssure with the data passed in to Pipeline.process"""


class Data(object):
    """Object to batch lists or arrays as block processable data

    Attributes:
        var_name(str): the name of the variable
        data (any type): the raw data
    """
    def __init__(self, var_name, data):
        """instantiates the Data object

        Args:
            var_name(str): the name of the variable
            data (any type): the raw data
        """
        # check if the data is in a valid container so we won't throw errors
        if not all(hasattr(container, req) for req in REQUIRED_CONTAINER_ATTRS):
            msg = INVALID_CONTAINER_MSG.format(
                                            input_name=var_name,
                                            con_methods=REQUIRED_CONTAINER_ATTRIBUTES)
            raise ArgTypeError(msg)

        self.var_name = var_name
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
