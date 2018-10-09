#
# @Email:  jmaggio14@gmail.com
#
# MIT License: https://github.com/jmaggio14/imsciutils/blob/master/LICENSE
#
# Copyright (c) 2018 Jeff Maggio, Nathan Dileas, Ryan Hartzell
#
from .Printer import get_printer
from .Exceptions import InvalidBlockInput
from .Exceptions import InvalidProcessingStrategy
from .Exceptions import InvalidLabelStrategy
from .Exceptions import DataLabelMismatch

def simple_block(process_fn,
                    input_shape,
                    output_shape,
                    name=None):
    """convienence function to make simple blocks

    Args:
        process_fn(func): function that takes in and processes
            exactly one datum
        input_shape(tuple): tuple of acceptable input shapes
        output_shape(tuple): tuple of acceptable output shapes
        name(str): name for this block, it will be automatically created/modified
            to make sure it is unique

    Returns:
        block(iu.SimpleBlock): simple block that applies the given function

    Example:
        >>> import imsciutils as iu
        >>> def calculate_orb_features(datum):
        ...     _,des = cv2.ORB_create().detectAndCompute(datum,None)
        ...     return des
        >>>
        >>> block = iu.simple_block(calculate_orb_features,
        ...                         input_shape=[None,None],
        ...                         output_shape=[None,32])
        >>>
    """

    if name is None:
        name = process_fn.__name__
    process_fn = staticmethod(process_fn)
    block_cls = type(name,(SimpleBlock,),{'process':process_fn})
    block =  block_cls(input_shape=input_shape,
                        output_shape=output_shape,
                        name=name)
    return block




class BaseBlock(object):
    """BaseBlock object which is the root class for all Block subclasses

    This is the _building block_ (pun intended) for the entire imsciutils
    pipelining system. All Blocks, both Simple and Batch blocks, will inherit
    from this object. Which contains base functionality to setup a block's
    printers, unique name, standard input/output_shapes and special functions
    for pipeline objects to call

    Args:
        input_shape(tuple): tuple of acceptable input shapes
        output_shape(tuple): tuple of acceptable output shapes
        name(str): name for this block, it will be automatically created/modified
            to make sure it is unique
        requires_training(bool): whether or not this block will require
            training

    Attributes:
        input_shape(tuple): tuple of acceptable input shapes
        output_shape(tuple): tuple of acceptable output shapes
        name(str): unique name for this block
        requires_training(bool): whether or not this block will require
            training
        trained(bool): whether or not this block has been trained, True
            by default if requires_training = False
        printer(iu.Printer): printer object for this block,
            registered to 'name'

    """
    EXTANT = {}
    def __init__(self,
                    input_shape,
                    output_shape,
                    name=None,
                    requires_training=False,
                    ):
        # ----------- building a unique name for this block ------------
        if name is None:
            name = self.__class__.__name__

        # JM: keeping track of names in base class variable
        if name in self.EXTANT:
            self.EXTANT[name] += 1
        else:
            self.EXTANT[name] = 1
        name = name + str(self.EXTANT[name])

        # ------ making input/output types lists of shapes --------
        if isinstance(input_shape,(list,tuple)):
            # JM:
            # check if there is more than one shape
            # if not, then put it in another list
            # (this makes comparison easier later)
            if not isinstance(input_shape[0],(list,tuple)):
                input_shape = [input_shape]
        else:
            # if it's not already a list or tuple, then put it in one
            input_shape = [input_shape]

        if isinstance(output_shape,(list,tuple)):
            # JM:
            # check if there is more than one shape
            # if not, then put it in another list
            # (this makes comparison easier later)
            if not isinstance(output_shape[0],(list,tuple)):
                output_shape = [output_shape]
        else:
            # if it's not already a list or tuple, then put it in one
            output_shape = [output_shape]


        self.input_shape = tuple(input_shape)
        self.output_shape = tuple(output_shape)
        self.name = name
        self.requires_training = requires_training

        self.trained = False
        if not self.requires_training:
            self.trained = True

        self.printer = get_printer(self.name)

        # JM:
        # update docstring with default values for input_shape, output_shape
        # training_status
        # self.__doc__ += \
        # """
        # Shapes:
        #     input_shapes:{}
        #     output_shapes:{}
        #
        # Training:
        #     requires_training: {}
        # """.format(self.input_shape,self.output_shape,self.requires_training)

    def train(self,data,labels=None):
        """(optional overload)trains the block if required

        users are expected to save pertinent variables as instance
        variables

        Args:
            data(list): list of datums to train on
            labels(list,None): corresponding label for each datum,
                None by default (for unsupervised systems)

        Returns:
            None
        """
        pass

    def before_process(self,data,labels=None):
        """(optional overload)function that runs before processing for
        optional functionality. this function takes in the full data list and
        label list. does nothing unless overloaded

        Args:
            data(list): list of datums to process
            labels(list,None): corresponding label for each datum,
                None by default (for unsupervised systems)
        """
        pass

    def after_process(self):
        """
        (optional overload)function that runs after processing for
        optional functionality. intended for optional use as a cleanup
        function

        Args:
            None
        """
        pass

    def _pipeline_train(self,data,labels=None):
        """function pipeline calls to train this block, modifies
        self.trained status

        Args:
            data(list): list of datums to train on
            labels(list,None): corresponding label for each datum,
                None by default (for unsupervised systems)

        Returns:
            None
        """
        self.train(self,data,labels)
        self.trained = True

    def _pipeline_process(self,data,labels=None):
        """function pipeline calls to process data using this block
        works with BatchBlocks and SimpleBlocks

        Args:
            data(list): list of datums to process
            labels(list,None): corresponding label for each datum,
                None by default (for unsupervised systems)

        Returns:
            processed(list): list of processed datums
            labels(list): list of corresponding labels for processed

        Raises:
            InvalidBlockInput: if data is not a list or tuple
            InvalidProcessingStrategy: if processed output is not a list
            InvalidLabelStrategy: if labels output is not a list
            DataLabelMismatch: if there is mismatch in the number of labels
                and processed datums

        """
        if labels is None:
            labels = [None] * len(data)

        if not isinstance(data,list):
            error_msg = "input data into a block must be a list"
            self.printer.error(error)
            raise InvalidBlockInput(self)

        #running prep function
        self.before_process(data,labels)

        # processing data and labels
        processed = self.process_strategy(data)
        labels = self.label_strategy(labels)

        # error checking for output types
        if not isinstance(processed,list):
            raise InvalidProcessStrategy(self)

        if not isinstance(labels,list):
            raise InvalidLabelStrategy(self)

        # making sure that we always have the same number of labels and datums
        if len(processed) != len(labels):
            raise DataLabelMismatch(processed,labels)

        # running post-process / cleanup function
        self.after_process()

        return processed, labels

    def process_strategy(self,data):
        """overarching processing management function for this block

        Args:
            data(list): list of datums to process

        Returns:
            processed (list): processed datums
        """
        raise NotImplementedError("'process_strategy' must be overloaded in all children")

    def label_strategy(self,labels):
        """overarching label management function for this block

        Args:
            labels(list,None): corresponding label for each datum,
                None by default (for unsupervised systems)

        Returns:
            labels (list): labels for datums (Nones for unsupervised systems)
        """
        raise NotImplementedError("'label_strategy' must be overloaded in all children")



class SimpleBlock(BaseBlock):
    """Block subclass that processes individual datums separately
    (as opposed to processing all data at once in a batch). This makes it useful
    for most CPU bound processing tasks as well as most functions in traditional
    computer vision that don't require an image sequence to process data

    Args:
        input_shape(tuple): tuple of acceptable input shapes
        output_shape(tuple): tuple of acceptable output shapes
        name(str): name for this block, it will be automatically created/modified
            to make sure it is unique
        requires_training(bool): whether or not this block will require
            training

    Attributes:
        input_shape(tuple): tuple of acceptable input shapes
        output_shape(tuple): tuple of acceptable output shapes
        name(str): unique name for this block
        requires_training(bool): whether or not this block will require
            training
        trained(bool): whether or not this block has been trained, True
            by default if requires_training = False
        printer(iu.Printer): printer object for this block,
            registered to 'name'

    """
    def process(self,datum):
        """(required overload)processes a single datum

        Args:
            datum: datum to process

        Returns:
            processed: datum processed by this block
        """
        raise NotImplementedError("'process' must be overloaded in all children")

    def label(self,lbl):
        """(optional overload)retrieves the label for this datum"""
        return lbl

    def process_strategy(self,data):
        """processes each datum using self.process and return list"""
        return [self.process(datum) for datum in data]

    def label_strategy(self,labels):
        """calls self.label for each datum and returns a list"""
        return [self.label(lbl) for lbl in labels]

    def __str__(self):
        return "{}-(SimpleBlock)".format(self.name)

    def __repr__(self):
        return str(self)




class BatchBlock(BaseBlock):
    """Block subclass that processes datums as a batch
    (as opposed to processing each datum individually). This makes it useful
    for GPU accelerated tasks where processing data in batches frequently
    increases processing speed. It can also be used for algorithms that
    require working with a full image sequence.

    Args:
        input_shape(tuple): tuple of acceptable input shapes
        output_shape(tuple): tuple of acceptable output shapes
        name(str): name for this block, it will be automatically created/modified
            to make sure it is unique
        requires_training(bool): whether or not this block will require
            training

    Attributes:
        input_shape(tuple): tuple of acceptable input shapes
        output_shape(tuple): tuple of acceptable output shapes
        name(str): unique name for this block
        requires_training(bool): whether or not this block will require
            training
        trained(bool): whether or not this block has been trained, True
            by default if requires_training = False
        printer(iu.Printer): printer object for this block,
            registered to 'name'

    """
    def batch_process(self,data):
        """(required overload)processes a list of data using this block's
        algorithm

        Args:
            data(list): list of datums to process

        Returns:
            process(list): list of processed datums
        """
        raise NotImplementedError("'batch_process' must be overloaded in all children")

    def labels(self,labels):
        """(optional overload) returns all labels for input datums"""
        return labels

    def process_strategy(self,data):
        """runs self.batch_process"""
        return self.batch_process(data)

    def label_strategy(self,labels):
        """runs self.labels"""
        return self.labels(labels)

    def __str__(self):
        return "{}-(BatchBlock)".format(self.name)

    def __repr__(self):
        return str(self)

# END
