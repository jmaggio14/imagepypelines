.. defining a raw html role
.. role:: raw-html(raw)
    :format: html

.. defining hyperlinks Substitutions
.. _MIT: https://choosealicense.com/licenses/mit/

.. _XKCD: https://imgs.xkcd.com/comics/data_pipeline.png

.. _logging: https://docs.python.org/3.7/library/logging.html

.. _build opencv from source: https://docs.opencv.org/3.4/df/d65/tutorial_table_of_content_introduction.html

.. _docker images: https://hub.docker.com/r/imagepypelines/imagepypelines-tools

.. _Chester F. Carlson Center for Imaging Science: https://www.cis.rit.edu/

.. _RIT: https://www.rit.edu/

.. _install Docker: https://docs.docker.com

.. _Python: https://www.python.org

.. add in the header image

.. image:: https://raw.githubusercontent.com/jmaggio14/imagepypelines/develop/docs/images/ip_logo_mini.png
  :align: center
  :alt: ip_logo

:raw-html:`<h1 align="center">ImagePypelines</h1>`

ImagePypelines is a package built by imaging scientists for imaging scientists.
It contains a simplistic front-end interface to construct complex image
processing pipelines, while automatically performing error checking,
task management and ultimately decreasing development time for many imaging and
data analysis projects.

ImagePypelines is developed by alumni of RIT_'s `Chester F. Carlson Center for
Imaging Science`_ who currently work in imaging related research or industries.

**ImagePypelines is currently in Alpha**

.. toctree:: about.rst
    :maxdepth: 2

.. toctree:: installation.rst
    :maxdepth: 2

.. toctree:: tutorials.rst
    :maxdepth: 2

.. toctree:: examples.rst
    :maxdepth: 2

.. toctree:: modules.rst
    :maxdepth: 2

.. toctree:: changelog.rst
    :maxdepth: 2


What Makes Us Unique?
*********************

The Pipeline
^^^^^^^^^^^^

ImagePypelines's most powerful feature is a high level interface to create data processing pipelines. These are objects which apply a sequence of algorithms to input data automatically, all while handling the nuance of data shape or type seamlessly.

In our experience as imaging scientists, processing pipelines in both corporate or academic settings are not always easy to adapt for new purposes and are therefore too often relegated solely to *proof-of-concept* applications. Many custom pipelines may also lack step-by-step error checking, which can make debugging a challenge.

.. image:: https://imgs.xkcd.com/comics/data_pipeline.png
  :alt: cracked pipelines
  :align: center


The **Pipeline** object of ImagePypelines allows for quick construction and prototyping, ensures end-to-end compatibility through each layer of a workflow, and leverages helpful in-house debugging utilities for use in image-centric or high-dimensional data routines.


The Block
^^^^^^^^^
Pipelines in ImagePypelines are constructed of processing `blocks` which apply an algorithm to a sequence of data passed into it.

.. image:: https://raw.githubusercontent.com/jmaggio14/imagepypelines/91b5f297632df16c2c246492782e37ea0a263b45/docs/images/pipeline-example.png
    :alt: pipeline diagram
    :align: center

Each **Block** takes in a list of data and returns a list of data, passing it onto the next block or out of the pipeline. This system ensures that blocks are compatible with algorithms that process data in batches or individually. Blocks also support label handling, and thus are **compatible with supervised machine learning systems or other algorithms that require training**

Broadly speaking, each box can be thought of as a black box which applies an operation to input data while handling nuances such as shape or data-type.

.. image:: https://raw.githubusercontent.com/jmaggio14/imagepypelines/91b5f297632df16c2c246492782e37ea0a263b45/docs/images/block.png
    :alt: block diagram
    :align: center

A **Datum** can be anything: an image array, a filename, a data label -- pretty much any pythonic type.


Blocks can also output more or less datums than they take in and are thus capable of being used for culling or injecting data into the pipeline.

Hang on - are all blocks compatible with one another?
"""""""""""""""""""""""""""""""""""""""""""""""""""""
Not entirely, each block has predefined acceptable inputs and outputs. However the `Pipeline` object will validate the pipeline integrity before any data is processed.

Processing Blocks Built into ImagePypelines
"""""""""""""""""""""""""""""""""""""""""""

More are being added with every commit, but here's what we've got packaged with ImagePypelines so far!

I/O Operations
--------------
- Image Display
- Camera Capture
- Image Loader
- Image Writing

Image Processing
----------------
- Colorspace Conversion
- Fast Fourier Transform
- Frequency Filtering
- Otsu Image Segmentation
- ORB Keypoints and Descriptors
- Image Resizing

Machine Learning
----------------
- Linear Support Vector Machine
- Rbf Support Vector Machine
- Poly Support Vector Machine
- Sigmoid Support Vector Machine
- Trainable Neural Networks
- 8 Pretrained Neural Networks (for feature extraction)
- Principle Component Analysis


Doing It Yourself!
******************

At the end of the day, we want our users to be able to generate *their own* content that works in an interconnected way with other blocks, pipelines, and custom workflows that aren't part of vanilla ImagePypelines. So how do you get started? Well, to begin, think of these best practices as ImagePypelines' PYP to Python_'s PEP ;)

Designing Processing Blocks
^^^^^^^^^^^^^^^^^^^^^^^^^^^

There are two ways to create a block:

1) Quick Block Creation
"""""""""""""""""""""""
For operations that can be completed in a single function that
accepts one datum, you can create a block with a single line.

.. .. code-block:: python
..
..   >>> import imagepypelines as ip
..   >>>
..   >>> # Create the function we use to process images
..   >>> def normalize_image(img):
..   ...   return img / img.max()
..   >>>
..   >>> # Set up the block to work with grayscale and color imagery (Note the type and size mappings)
..   >>> io_map = {ip.ArrayType([None,None]):ip.ArrayType([None,None]),
..   ...       ip.ArrayType([None,None,3]):ip.ArrayType([None,None,3])}
..   >>>
..   >>> # Instantiate a quick block using your processing func and io_map
..   >>> block = ip.quick_block(normalize_image, io_map)


2) Object Inheritance
"""""""""""""""""""""

Another method is to set up your block by object inheritance, also known as a subclass. This is the preferred, flexible method of setting up your own blocks for use, however it's a little more legwork. Therefore, this is covered in more detail on our tutorial pages. Such topics as training and label handling for machine learning applications can also be found on our tutorial pages.

.. code-block:: python

  import imagepypelines as ip

  # Note that we inherit from ip.SimpleBlock
  class NormalizeBlock(ip.SimpleBlock):
  	"""Normalize block between 0 and max_count, inclusive"""

    def __init__(self, max_count=1):

      self.max_count = max_count

  		# set up the block to work with grayscale and color imagery
  		io_map = {ip.ArrayType([None,None]):ip.ArrayType([None,None]),
  					ip.ArrayType([None,None,3]):ip.ArrayType([None,None,3])}

  		super(NormalizeBlock,self).__init__(io_map)

  	def process(self,img):
  		"""Overload the processing function for this block"""

      return img.astype(np.float32) / img.max() * self.max_count

Designing Pipelines
^^^^^^^^^^^^^^^^^^^
Now that you've gotten a sense of how blocks are structured, here's a brief look at creating your very own pipeline. After all, building a pipeline is super easy!

Image Display Pipeline
""""""""""""""""""""""

.. code-block:: python

  import imagepypelines as ip

  # This is how a Pipeline object is instantiated
  pipeline = ip.Pipeline(name='image display')

  # Each one of these elements adds a Block object to our pipeline
  pipeline.add(ip.ImageLoader())
  pipeline.add(ip.Resizer())
  pipeline.add(ip.BlockViewer())

  # now let's display some example data!
  pipeline.process(ip.standard_image_filenames())

Voila! We've just made a processing pipeline that can read in images, resize them, and display them! But we can do much more complicated operations.

Lowpass Filter Pipeline
"""""""""""""""""""""""

.. code-block:: python

  import imagepypelines as ip

  load = ip.ImageLoader()
  resize = ip.Resizer(512,512)
  fft = ip.FFT()
  lowpass = ip.Lowpass(cut_off=32)
  ifft = ip.IFFT()
  display = ip.BlockViewer(pause_time=1)

  pipeline = ip.Pipeline(blocks=[load, resize, fft, lowpass, ifft, display])

  # process a set of images (using imagepypelines' example data)
  filenames = ip.standard_image_filenames()
  pipeline.process(filenames)

This pipeline takes in a set of standard images, resizes them, performs an FFT, applies a lowpass filter in frequency space, performs an inverse FFT, and displays them!

Machine Learning Applications
"""""""""""""""""""""""""""""
One of the more powerful applications of ImagePypelines is it's ease of use in
*machine learning* and *feature engineering* applications.
We can easily tailor a pipeline to perform image classification, for example.

This classifier is available as a built-in pipeline with fully tweakable hyperparameters as `ip.SimpleImageClassifier`.

.. code-block:: python

  import imagepypelines as ip

  features = ip.PretrainedNetwork() # image feature block
  pca = ip.PCA(256) # principle component analysis block
  neural_network = ip.MultilayerPerceptron(neurons=512, num_hidden=2) # neural network block

  classifier = ip.Pipeline([features,pca,neural_network])

  # loading example data
  cifar10 = ip.Cifar10()
  train_data, train_labels = cifar10.get_train()
  test_data, ground_truth = cifar10.get_test()

  classifier.train(train_data,train_labels) # train the classifier
  predictions = classifier.process(test_data) # test the classifier

  # print the accuracy
  accuracy = ip.accuracy(predictions,ground_truth) * 100
  print('pipeline classification accuracy is {}%!'.format(accuracy))


We just trained a full neural network classifier!

Head on over to our tutorials page for more in depth intros to how ImagePypelines can be a useful tool for you!
