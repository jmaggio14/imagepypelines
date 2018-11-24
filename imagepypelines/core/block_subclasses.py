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

    def __init__(self,*args,**kwargs):
        # inherit from super
        super(TfBlock,self).__init__(*args,**kwargs)
        self.fetches = []
        self.data_fetch_name = "batch_data"
        self.label_fetch_name = "labels"
        self.graph, self.sess = self._setup_graph_wrapper()

    # JM: called in __init__
    def _setup_graph_wrapper(self):
        # ----------- setup tf graph -------------
        graph = tf.Graph()
        batch_data = tf.placeholder(tf.float32,name=self.data_fetch_name)
        labels = tf.placeholder(tf.float32,name=self.label_fetch_name)

        with graph.as_default():
            ret = self.setup_graph(batch_data,labels)

        sess = tf.Session(graph=graph)

        # --------- error checking ret ---------
        error_msg = \
            "'setup_graph' must return <processed_tensor_name> "
                + "or (<processed_tensor_name>, <processed_label_name>)"
        # JM: checking to see if ret is a two element tuple
        # containing (processed_tensor_name, processed_label_name)
        # for using as sess.run fetches
        if isinstance(ret,(tuple,list)):
            self.printer.critical(error_msg)
            assert len(ret) == 2, error_msg
            self.fetches.extend(ret)
        # JM: checking to see if ret is one element
        # ie only the processed data fetch. see setup_graph docs
        else:
            self.fetches.append(ret)

        return graph,sess

    def setup_graph(self,data_placeholder,label_placeholder):
        """(required overload)sets up the tensorflow graph

        Args:
            data_placeholder(tf.placeholder): placeholder tensor into
                which data data will be fed during graph execution
            label_placeholder(tf.placeholder): placeholder tensor into
                which label data will be fed during graph execution

        Returns:
            fetches(str,tuple):
                1) the tensor name of the processed data, a fetch
                2) a two element tuple containing
                    (processed tensor name, label tensor name)
        """
        error_msg = "'setup_graph' must be overloaded in all children"
        raise NotImplementedError(error_msg)


    def before_process(self, batch_data, batch_labels=None):
        feed_dict = {
                        self.data_fetch_name:batch_data,
                        self.label_fetch_name:batch_labels
                        }
        # if setup graph only returned the processed data name,
        # then auto append the tensor name of the labels that were fed
        if len(self.fetches) == 1:
            self.fetches.append(self.label_fetch_name + ':0')

        # process data through the graph and fetch the tensors which
        # contained processed and label data
        processed,labels = self.sess.run(self.fetches,feed_dict=feed_dict)

        # unstacking the data and returning a list
        self.processed = [processed[i] for i in range(processed.shape[0])]
        self.labels = [labels[i] for i in range(labels.shape[0])]

    def batch_process(self,data):
        return self.processed

    def labels(self,labels):
        return self.labels

    def prep_for_serialization(self):
        # create saver object
        saver = tf.train.Saver()

        # retrieve filename for the metadata cache
        self.sess_filename = metadata.filename(self.name + '.ckpt')
        msg = "this object will save pertinent data to {}. Keep this in mind "
                + "if you are transferring this pipeline to a different machine"
                .format(self.sess_filename)

        self.printer.warning(msg)
        saver.save(self.sess_filename)

        # delete GPU bound objects
        delattr(self,'sess')
        delattr(self,'graph')

    def restore_from_serialization(self):
        # retore session and graph
        saver = tf.train.Saver()
        self.sess = saver.restore(self.sess_filename)
        self.graph = self.sess.graph

        # cleanup the metadata folder - delete the data associated with
        # this model
        metadata.remove(self.sess_filename)

        # delete the uneeded instance variable
        delattr(self,'sess_filename')




# END
