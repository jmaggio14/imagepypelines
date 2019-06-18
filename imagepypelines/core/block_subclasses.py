# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018-2019 Jeff Maggio, Nathan Dileas, Ryan Hartzell
#
import sys
from .BaseBlock import BaseBlock
from .imports import import_tensorflow
from abc import abstractmethod


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

    @abstractmethod
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

    @abstractmethod
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


class TfBlock(BatchBlock):
    """Subclass of BaseBlock designed to make working with tensorflow in
    imagepypelines more fluid.

    Users are expected to put all code related to your tensorflow graph in
    the setup_graph function, where it will be automatically added to the
    objects `graph` and `sess` variables

    training is left entirely up to the user through the use of overloading the
    `train` function.

    Do not overload the following functions unless you have read the source code
    and understand the consequences: _setup_graph_wrapper, before_process,
    batch_process, after_process, labels, prep_for_serialization,
    restore_from_serialization


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
        io_map(IoMap): object that maps inputs to this block to outputs,
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
    def __init__(self,*args,**kwargs):
        global tf
        tf = import_tensorflow()

        # inherit from super
        super(TfBlock,self).__init__(*args,**kwargs)

        # setup the graph
        self.fetches = []
        self.data_feed_name = "batch_data"
        self.label_feed_name = "labels"
        self.processed = None
        self.lbls = None
        self.graph, self.sess = self._setup_graph_wrapper()

    # JM: called in __init__
    def _setup_graph_wrapper(self):
        """Wrapper function to call the subclass defined function 'setup_graph'.
        this function will ensure that all tensorflow graph code is saved to a
        custom graph and session object - this is to ensure that multiple
        tf graphs can be operated by different blocks in the pipeline.

        Args:
            None

        Returns:
            tf.Session : the session for this block, this will be saved to
                self.sess
            tf.Graph : the processing graph for this block, this will be saved
                to self.graph
        """
        # ----------- setup tf graph -------------
        graph = tf.Graph()
        with graph.as_default():
            batch_data = tf.placeholder(tf.float32,name=self.data_feed_name)
            labels = tf.placeholder(tf.float32,name=self.label_feed_name)
            ret = self.setup_graph(batch_data,labels)

        sess = tf.Session(graph=graph)

        # --------- error checking ret ---------
        error_msg = "'setup_graph' must return <processed_tensor_name> "\
                    + "or (<processed_tensor_name>, <processed_label_name>)"
        # JM: checking to see if ret is a two element tuple
        # containing (processed_tensor_name, processed_label_name)
        # for using as sess.run fetches
        if isinstance(ret,(tuple,list)):
            assert len(ret) == 2, error_msg
            self.fetches.extend(ret)
        # JM: checking to see if ret is one element
        # ie only the processed data fetch. see setup_graph docs
        else:
            # if setup graph only returned the processed data name,
            # then auto append the tensor name of the labels that were fed
            self.fetches.append(ret) # append <processed_tensor_name>
            if len(self.fetches) == 1:
                self.fetches.append(self.label_feed_name+':0')

        return graph, sess

    @abstractmethod
    def setup_graph(self,data_placeholder,label_placeholder):
        """(required overload)sets up the tensorflow graph that will be used to
        execute code for this block

        Args:
            data_placeholder(tf.placeholder): placeholder tensor into
                which data data will be fed during graph execution
            label_placeholder(tf.placeholder): placeholder tensor into
                which label data will be fed during graph execution

        Returns:
            (str,tuple): fetches - one of
                1) Tensor name of the processed data: <processed tensor name>
                2) A two element tuple containing
                    (<processed tensor name>, <label tensor name>)
        """
        error_msg = "'setup_graph' must be overloaded in all children"
        raise NotImplementedError(error_msg)


    def before_process(self, batch_data, batch_labels=None):
        """Processes the data through the tensorflow graph and makes the fetched
        data available as instance variables in this block. The tensors returned
        by this function are determined by the output of the overloaded
        setup_graph function

        This function will feed data into the data and label placeholder tensors
        and fetch the processed data and label tensors specified by the output
        of the setup_graph function

        Saves processed data and labels to instance variables so they can
        be returned in batch_process and labels functions

        Args:
            batch_data (list): list of datums to process in this tensorflow
                graph
            batch_labels (list): list of labels for this graph

        Returns:
            None
        """
        feed_dict = {
                        self.data_feed_name+':0':batch_data,
                        self.label_feed_name+':0':batch_labels
                        }

        # process data through the graph and fetch the tensors which
        # contained processed and label data
        processed,labels = self.sess.run(self.fetches,feed_dict=feed_dict)

        # unstacking the data and returning a list
        self.processed = [processed[i] for i in range(processed.shape[0])]
        self.lbls = [labels[i] for i in range(labels.shape[0])]

    def batch_process(self,data):
        """returns the processed data retrieved from the tensorflow graph in
        'before_process'

        Args:
            data (list): list of raw data to process (not used in this
                function in a TfBlock)

        Returns:
            data (list): list of processed data for the next block
        """
        return self.processed

    def labels(self,labels):
        """returns the labels retrieved from the tensorflow graph in
        'before_process'

        Args:
            labels (list): list of raw labels to process (not used in this
                function in a TfBlock)

        Returns:
            labels (list): list of processed labels for the next block
        """
        return self.lbls

    def after_process(self):
        """reduces object memory footprint by setting 'processed' and 'labels'
        variables to None"""
        self.processed = None
        self.lbls = None

    def prep_for_serialization(self):
        with tf.Session(graph=self.graph) as sess:
            init_op = tf.initialize_all_variables()
            sess.run(init_op)

            # create saver object
            saver = tf.train.Saver()

            # retrieve filename for the metadata cache
            self.sess_filename = metadata.filename(self.name)
            msg = "this object will save pertinent data to {}. Keep this in mind "\
                + "if you are transferring this pipeline to a different machine"\
                    .format(self.sess_filename)

            self.printer.warning(msg)
            saver.save(sess, self.sess_filename)

        # delete GPU bound objects
        del self.sess
        del self.graph

    def restore_from_serialization(self):
        # retore session and graph
        saver = tf.train.Saver()
        self.sess = saver.restore(self.sess_filename)
        self.graph = self.sess.graph

        # cleanup the metadata folder - delete the data associated with
        # this model
        metadata.remove(self.sess_filename)

        # delete the uneeded instance variable
        del self.sess_filename




# END
