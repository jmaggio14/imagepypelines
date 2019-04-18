=========
Tutorials
=========

.. contents::
    :depth: 3

building your own pipeline
**************************

Pipelines are constructed of `blocks` which are simply objects that take in data,
process it, and output the processed data. Pipelines simply provide a high level
interface to control and apply processing algorithms for your workflows.

.. image:: https://raw.githubusercontent.com/jmaggio14/imagepypelines/91b5f297632df16c2c246492782e37ea0a263b45/docs/images/pipeline-example.png
    :align: center

let's create an example fourier transform pipeline
--------------------------------------------------

.. doctest:: python

    >>> import imagepypelines as ip
    >>>
    >>> loader = ip.blocks.ImageLoader() # load in image filenames
    >>> grayscale = ip.blocks.Color2Gray() # convert images to grayscale
    >>> fft = ip.blocks.FFT() # create an fft
    >>>
    >>> fft_pipeline = ip.Pipeline([loader,grayscale,fft])
    >>>
    >>> # load in a list of example image filenames
    >>> filenames = ip.standard_image_filenames()
    >>> # process the data
    >>> ffts = fft_pipeline.process(filenames) # doctest: +ELLIPSIS
    --ANY--
    >>>

Simple Input Output Operations
------------------------------

Most blocks built into `imagepypelines` are made to work with imagery, but pipelines
are equally capable of performing IO output operations

loading images, process them, and saving them to disk
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Thresholding pipeline, read images off of the disk, perform otsu thresholding,
and then save them to disk


.. doctest:: python

    >>> import imagepypelines as ip
    >>>
    >>> # build blocks for this pipeline
    >>> loader = ip.blocks.ImageLoader()
    >>> rgb2gray = ip.blocks.Color2Gray()
    >>> otsu = ip.blocks.Otsu()
    >>> writer = ip.blocks.WriterBlock('./output_dir',return_type='filename')
    >>>
    >>> # pipeline construction
    >>> pipeline = ip.Pipeline([loader,rgb2gray,otsu,writer])
    >>>
    >>> # get filenames of saved thresholded data
    >>> processed_filenames = pipeline.process( ip.standard_image_filenames() )  # doctest:+ELLIPSIS
    --ANY--


Pulling imagery off of a webcam and injecting it directly into a pipeline
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
This is also a good example of how blocks can inject data into a pipeline.
A block with a single input can result in N outputs

.. doctest:: python
    :skipif: IP_NO_CAMERA

    >>> import imagepypelines as ip
    >>>
    >>> # let's make a pipeline to talk to a webcam and save them to disk
    >>> camera = ip.blocks.CameraBlock(device='/dev/video0')
    >>> rgb2gray = ip.blocks.Color2Gray()
    >>> otsu = ip.blocks.Otsu()
    >>> writer = ip.blocks.WriterBlock(output_dir='./output_dir')
    >>>
    >>> # pipeline construction
    >>> pipeline = ip.Pipeline(blocks=[camera,otsu,writer])
    >>>
    >>> # run capture 100 images in increments of 10
    >>> for i in range(10):
    ...     pipeline.process([10]) # doctest:+ELLIPSIS
    --ANY--

Machine Learning Applications
-----------------------------
One of the more powerful applications of ImagePypelines is its ease of use in
*machine learning* and *feature engineering* applications. We can easily build
a simple image classifier that is tailored to your purposes

Classification using a neural network
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
You can tweak this example with your own image data and hyperparameters to make a classifier for your own applications.
*this classifier is available as a builtin Pipeline with fully tweakable hyperparameters as ip.SimpleImageClassifier*

.. doctest:: python

    >>> import imagepypelines as ip
    >>>
    >>> # ----------------- loading example data ---------------
    >>> cifar10 = ip.ml.Cifar10(fraction=.01)
    >>> train_data, train_labels = cifar10.get_train()
    >>> test_data, ground_truth = cifar10.get_test()
    >>>
    >>> # --------------- now we'll build the pipeline ----------------
    >>> features = ip.blocks.PretrainedNetwork() # image feature block
    >>> pca = ip.blocks.PCA(256) # principle component analysis block
    >>> neural_network = ip.blocks.MultilayerPerceptron(neurons=512, num_hidden=2) # neural network block
    >>>
    >>> classifier = ip.Pipeline([features,pca,neural_network])
    >>>
    >>> # -------------- train and predict the classifier ---------------
    >>> classifier.train(train_data,train_labels) # train the classifier #doctest:+ELLIPSIS
    --ANY--
    >>> predictions = classifier.process(test_data) # doctest:+ELLIPSIS
    --ANY--
    >>> # print the accuracy
    >>> accuracy = ip.accuracy(predictions,ground_truth)
    >>> print('accuracy: {}%'.format(accuracy * 100) ) # doctest:+ELLIPSIS
    accuracy: --ANY--%

Classification using a Support Vector Machine
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doctest:: python

    >>> import imagepypelines as ip
    >>>
    >>> # ----------------- loading example data ---------------
    >>> cifar10 = ip.ml.Cifar10(fraction=.01)
    >>> train_data, train_labels = cifar10.get_train()
    >>> test_data, ground_truth = cifar10.get_test()
    >>>
    >>> # --------------- now we'll build the pipeline ----------------
    >>> features = ip.blocks.PretrainedNetwork() # image feature block
    >>> pca = ip.blocks.PCA(256) # principle component analysis block
    >>> neural_network = ip.blocks.LinearSvm() # support vector machine block
    >>> # SVMs for linear, rbf, polynomial, and sigmoid kernels are all available
    >>>
    >>> classifier = ip.Pipeline([features,pca,neural_network])
    >>>
    >>> # -------------- train and predict the classifier ---------------
    >>> classifier.train(train_data,train_labels) # train the classifier #doctest:+ELLIPSIS
    --ANY--
    >>> predictions = classifier.process(test_data) # doctest:+ELLIPSIS
    --ANY--
    >>>
    >>> # print the accuracy
    >>> accuracy = ip.accuracy(predictions,ground_truth)
    >>> print('accuracy: {}%'.format(accuracy * 100) ) # doctest:+ELLIPSIS
    accuracy: --ANY--%

Creating your own block
***********************
There are two types of blocks in ImagePypelines: **Simple Blocks** - blocks that process one piece of data at a time, and **Batch Blocks** - blocks that process multiple pieces of data at a time.

In practical terms, this merely manifests itself as a function that takes a list of data *(batch blocks)* or a function that takes in a single datum *(simple blocks)*

Batch Blocks
------------
Batch processing *(the act of processing multiple pieces of data at the same time)* is typically used when you are utilizing GPUs or other types of hardware acceleration in your processing pipeline.

They can make your pipelines **much** more efficient, this is typically because sending data between the *CPU* & *GPU* is slow process. Sending 100 images separately is slower than sending 100 images at once. Practically, all this really means is that having a system capable of processing multiple pieces of data can optimize your pipeline.

Batch Processing blocks in ImagePypelines simply contain a processing function that takes in a list of data and returns a list of data.

Lets create a super simple example just to demonstrate how you can create a batch processing block in ImagePypelines.

.. testcode:: python

    import imagepypelines as ip
    import numpy as np

    class AddOneBlock(ip.BatchBlock):
        def __init__(self):
            io_map = {ip.RGB:ip.RGB,
                          ip.GRAY:ip.GRAY}
            super(AddOneBlock,self).__init__(io_map)
        def batch_process(self,batch_data):
            """take in a list of datums and return a processed list of datums"""
            # turn this list of data into a single array
            img_stack = np.stack(batch_data, axis=0) # [(N,M,3),(N,M,3)] --> (2,N,M,3)
            img_stack = img_stack + 1 # add one to images
            # (2,N,M,3) --> [(N,M,3),(N,M,3)]
            processed_batch = [img_stack[i] for i in range(img_stack.shape[0])]
            return processed_batch

    p = ip.Pipeline( [AddOneBlock()] )
    std_images_plus_one = p.process( ip.standard_images() )
