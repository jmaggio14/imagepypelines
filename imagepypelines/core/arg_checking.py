from .Exceptions import ArgTypeError

from abc import ABCMeta, abstractmethod
import numpy as np




################################################################################
class ArgType(metaclass=ABCMeta):
    def __init__(self, obj_type, containers):
        """instantiates the ArgType

        Args:
            obj_type(:obj:`tuple` of :obj:`type`,type): the type of object this
                ArgType should be
            containers(:obj:`tuple` of :obj:`tuple`): list or tuple of container
                types
        """

        self.obj_type = obj_type
        # NOTE: maybe do a check to ensure shape is a list of lists?
        self.containers = containers

    ############################################################################
    def validate(self, batch, batch_size):
        """by default, just checks that datums in the batch are the correct type"""
        # all we do is check that is every datum in the batch is a string
        if self.batch_size == "singles":
            datum = batch
            return isinstance(datum, self.obj_type)
        else:
            return all( isinstance(datum,self.obj_type) for datum in batch )



################################################################################
#                               Default ArgTypes
################################################################################
class Array(ArgType):
    def __init__(self, shapes, containers, dtypes=None):
        """instantiates the Array ArgTypes

        Args:
            shapes(:obj:`tuple` of :obj:`tuple`): list or tuple of data shapes
            containers(:obj:`tuple` of :obj:`tuple`): list or tuple of container
                types
            dtypes(:obj:`tuple` of :obj:`numpy.dtype`): list or tuple of numpy
                dtypes
        """
        self.shapes = shapes
        self.dtypes = dtypes
        super().__init__(np.ndarray, containers)

    ############################################################################
    def validate(self, batch, batch_size):
        """validates to make sure the data batch is compatible with our
        requirements. (called from the block)

        Args:
            batch(container): data batch to be passed into the block's process
                function
            batch_size(str,int): the batch_size specified for the block

        Returns:
            bool: whether or not the batch is compatible with the block's
                process argument
        """
        # if batch_size is "singles", then batch is actually just one datum
        if self.batch_size == "singles":
            datum = batch
            container_okay = True # container is irrelevant
        # we are dealing with a container of multiple datums
        else:
            # first we have to make sure the container is valid
            container_okay = isinstance(batch, self.containers)
            # *because this is an array*
            # we only have to check the shape of the first row - because all
            # rows will have the same shape
            datum = batch[0]

        # reject automatically if the container isn't compatible
        if not container_okay:
            return False

        # ensure datum is the correct type
        if not isinstance(datum, self.obj_type):
            return False

        # check if the dtype is compatible (default is yes)
        if not self.dtype_check(datum):
            return False

        # finally check the shape
        return self.shape_check(datum)

    ############################################################################
    def shape_check(self, datum):
        """checks the shape of the datum is compatible"""

        # any shape works if shape is None
        if self.shape is None:
            return True

        # iterate through acceptable shapes and make sure at least one fits
        for shape in self.shapes:
            # automatically reject this shape if the dimensionality is different
            if len(shape) != len(datum.shape):
                continue

            # if all the axes are compatible, then this shape is good
            if all(self.axis_check(s_ax, d_ax) for s_ax,d_ax in zip(shape,datum.shape) ):
                return True

        return False

    ############################################################################
    def dtype_check(self, datum):
        """checks if the datum's dtype is compatible. if dtypes are specified
        during instantiation, then this function returns True automatically"""
        if self.dtypes:
            return (datum.dtype in self.dtypes)
        # otherwise return true, because we don't have any dtype filters
        return True

    ############################################################################
    @staticmethod
    def axis_check(okay_axis, datum_axis):
        # if okay_axis is None, then any size will do
        if okay_axis is None:
            return True
        # otherwise we have to make sure the axis sizes are identical
        else:
            return (okay_axis == datum_axis)


################################################################################
class ArgNone(ArgType):
    """NoneType Argument Type for blocks"""
    def __init__(self, containers):
        """Instantiates ArgNone

        Args:
            containers(:obj:`tuple` of :obj:`tuple`): list or tuple of container
                types
        """
        super().__init__(type(None), containers)


################################################################################
class Str(ArgType):
    """String Argument Type for blocks"""
    def __init__(self, containers):
        """Instantiates Str

        Args:
            containers(:obj:`tuple` of :obj:`tuple`): list or tuple of container
                types
        """
        super().__init__(str, containers)


# NUMERICAL
################################################################################
class Num(ArgType):
    """Argument Type for either Ints or Floats"""
    def __init__(self, containers):
        """Instantiates Str

        Args:
            containers(:obj:`tuple` of :obj:`tuple`): list or tuple of container
                types
        """
        super().__init__((float,int), containers)


################################################################################
class Int(ArgType):
    """Int Argument Type for Blocks"""
    def __init__(self, containers):
        """Instantiates Str

        Args:
            containers(:obj:`tuple` of :obj:`tuple`): list or tuple of container
                types
        """
        super().__init__(int, containers)


################################################################################
class Float(ArgType):
    """Float Argument Type for Blocks"""
    def __init__(self, containers):
        """Instantiates Str

        Args:
            containers(:obj:`tuple` of :obj:`tuple`): list or tuple of container
                types
        """
        super().__init__(float, containers)


# ITERABLE TYPES
################################################################################
class BaseIterable(ArgType):
    """Base iterable type for List, Tuple, Set and Iterable Types"""
    def __init__(self, obj_type, length, containers):
        """Instantiates ArgNone

        Args:
            obj_type(:obj:`tuple` of :obj:`type`,type): the type of object this
                ArgType should be
            length(int): length of the iterable. If left as None, then no lengths
                checking will occur
            containers(:obj:`tuple` of :obj:`tuple`): list or tuple of container
                types
        """
        # make sure the length is the correct type
        if not (isinstance(length,int) or (length is None)):
            raise TypeError("'length must be None or an int, not %s'" % type(length))

        self.length = length
        super().__init__(obj_type, containers)

    ############################################################################
    def validate(self, batch, batch_size):
        """validates that the batch is of the correct type and length (if desired)

        Args:
            batch(container): data batch to be passed into the block's process
                function
            batch_size(str,int): the batch_size specified for the block

        Returns:
            bool: whether or not the batch is compatible with the block's
                process argument
        """
        if self.batch_size == "singles":
            datum = batch
            # make sure it's the correct iterable type
            if isinstance(datum, self.obj_type):
                # make sure datum is the correct length if it's defined
                if self.length:
                    return (len(datum) == self.length)
        else:
            # for every datum
            for datum in batch:
                # make sure that the datum is the correct object type
                if isinstance(datum, self.obj_type):
                    # make sure the datum is the correct length
                    if len(datum) != self.length:
                        return False
                else:
                    return False

        return True
################################################################################
class List(BaseIterable):
    def __init__(self, length, containers):
        """Instantiates List

        Args:
            length(int): length of the iterable. If left as None, then no lengths
                checking will occur
            containers(:obj:`tuple` of :obj:`tuple`): list or tuple of container
                types
        """
        super().__init__(list, length, containers)


################################################################################
class Tuple(BaseIterable):
    def __init__(self, length, containers):
        """Instantiates Tuple

        Args:
            length(int): length of the iterable. If left as None, then no lengths
                checking will occur
            containers(:obj:`tuple` of :obj:`tuple`): list or tuple of container
                types
        """
        super().__init__(tuple, length, containers)


################################################################################
class Set(BaseIterable):
    def __init__(self, length, containers):
        """Instantiates Set

        Args:
            length(int): length of the iterable. If left as None, then no lengths
                checking will occur
            containers(:obj:`tuple` of :obj:`tuple`): list or tuple of container
                types
        """
        super().__init__(set, length, containers)


################################################################################
class Iterable(BaseIterable):
    def __init__(self, length, containers):
        """Instantiates Iterable

        Args:
            length(int): length of the iterable. If left as None, then no lengths
                checking will occur
            containers(:obj:`tuple` of :obj:`tuple`): list or tuple of container
                types
        """
        super().__init__((list,tuple,set), length, containers)


# END
