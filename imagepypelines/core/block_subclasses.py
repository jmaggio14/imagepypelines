# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018 Jeff Maggio, Nathan Dileas, Ryan Hartzell
#
import sys
from .BaseBlock import BaseBlock


class SimpleBlock(BaseBlock):
    """Block subclass that processes individual datums separately
    (as opposed to processing all data at once in a batch). This makes it useful
    for most CPU bound processing tasks as well as most functions in traditional
    computer vision that don't require an image sequence to process data

    Args:

        io_map(IoMap,dict): dictionary of input-output mappings for this
            Block
        name(str): name for this block, it will be automatically created/modified
            to make sure it is unique
        notes(str): a short description of this block
        requires_training(bool): whether or not this block will require
            training
        requires_labels(bool): whether or not this block will require
            labels during training

    Attributes:

        io_map(IoMap): object that maps inputs to this block to outputs
            subclass of tuple where I/O is stored as:
            ( (input1,output1),(input2,output2)... )
        name(str): unique name for this block
        notes(str): a short description of this block
        requires_training(bool): whether or not this block will require
            training
        trained(bool): whether or not this block has been trained, True
            by default if requires_training = False
        printer(ip.Printer): printer object for this block,
            registered to 'name'

    """

    def process(self, datum):
        """(required overload)processes a single datum

        Args:
            datum: datum to process

        Returns:
            processed: datum processed by this block
        """
        raise NotImplementedError("'process' must be overloaded in all children")

    def label(self, lbl):
        """(optional overload)retrieves the label for this datum"""
        return lbl

    def process_strategy(self, data):
        """processes each datum using self.process and return list"""
        return [self.process(datum) for datum in data]

    def label_strategy(self, labels):
        """calls self.label for each datum and returns a list or Nonetype"""
        return [self.label(lbl) for lbl in labels]

    def __repr__(self):
        return (str(self) + '-(SimpleBlock)' + '\n' + self.notes)


class BatchBlock(BaseBlock):
    """Block subclass that processes datums as a batch
    (as opposed to processing each datum individually). This makes it useful
    for GPU accelerated tasks where processing data in batches frequently
    increases processing speed. It can also be used for algorithms that
    require working with a full image sequence.

    Args:

        io_map(IoMap,dict): dictionary of input-output mappings for this
            Block
        name(str): name for this block, it will be automatically created/modified
            to make sure it is unique
        notes(str): a short description of this block
        requires_training(bool): whether or not this block will require
            training
        requires_labels(bool): whether or not this block will require
            labels during training

    Attributes:

        io_map(IoMap): object that maps inputs to this block to outputs
            subclass of tuple where I/O is stored as:
            ( (input1,output1),(input2,output2)... )
        name(str): unique name for this block
        notes(str): a short description of this block
        requires_training(bool): whether or not this block will require
            training
        trained(bool): whether or not this block has been trained, True
            by default if requires_training = False
        printer(ip.Printer): printer object for this block,
            registered to 'name'

    """

    def batch_process(self, data):
        """(required overload)processes a list of data using this block's
        algorithm

        Args:
            data(list): list of datums to process

        Returns:
            process(list): list of processed datums
        """
        error_msg = "'batch_process' must be overloaded in all children"
        raise NotImplementedError(error_msg)

    def labels(self, labels):
        """(optional overload) returns all labels for input datums or None"""
        return labels

    def process_strategy(self, data):
        """runs self.batch_process"""
        return self.batch_process(data)

    def label_strategy(self, labels):
        """runs self.labels"""
        return self.labels(labels)

    def __repr__(self):
        return (str(self) + '-(BatchBlock)' + '\n' + self.notes)


class TfBlock(BatchBlock):
    def __new__(cls):
        global tf
        import tensorflow as tf
        return cls

    def __init__(self,
                     io_map,
                     name=None,
                     notes=None,
                     requires_training=False,
                     requires_labels=False,
                     ):

        # inherit from super
        super(TfBlock,self).__init__(io_map,
                                        name,
                                        notes,
                                        requires_training,
                                        requires_labels)
        # ----------- setup tf graph -------------
        self.graph = tf.Graph()
        with self.graph.as_default():
            ret = self.setup_graph()
        self.sess = tf.Session(graph=self.graph)

        # --- error checking ret ---
        if not isinstance(ret, tuple):
            self.printer.critical("'setup_graph' must return (fetches,feed_name)")
            exit(1)
        elif len(ret) != 2:
            self.printer.critical("'setup_graph' must return (fetches,feed_name)")
            exit(1)

        self.fetches, self.feed_name = ret

    def setup_graph(self):
        """(required overload)sets up the tensorflow graph

        Args:
            None

        Returns:
            fetches(str,list): tensors to extract
            feed_name(str): name of the tensor to feed batch_data into
        """
        error_msg = "'setup_graph' must be overloaded in all children"
        raise NotImplementedError(error_msg)


    def before_process(self, batch_data, batch_labels=None):
        self.processed = self.sess.run(self.fetches,
                                        feed_dict={self.feed_name: batch_data})

    def batch_process(self, batch_data):
        return self.processed


# END
