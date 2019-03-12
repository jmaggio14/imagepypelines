.. defining a raw html role
.. role:: raw-html(raw)
    :format: html

.. defining hyperlinks Substitutions
.. _Imagepypelines: http://www.imagepypelines.org/

.. _MIT: https://choosealicense.com/licenses/mit/

.. _XKCD: https://imgs.xkcd.com/comics/data_pipeline.png

.. _logging: https://docs.python.org/3.7/library/logging.html

.. _build opencv from source: https://docs.opencv.org/3.4/df/d65/tutorial_table_of_content_introduction.html

.. _docker images: https://hub.docker.com/r/imagepypelines/imagepypelines-tools

.. _Imaging Science Program: https://www.cis.rit.edu/

.. _RIT: https://www.rit.edu/

.. _install Docker: https://docs.docker.com

.. add in the header image

.. image:: https://raw.githubusercontent.com/jmaggio14/imagepypelines/develop/docs/images/ip_logo_mini.png
  :align: center
  :alt: ip_logo

:raw-html:`<h1 align="center">ImagePypelines</h1>`



.. image:: https://www.travis-ci.com/jmaggio14/imagepypelines.svg?branch=master
  :target: https://www.travis-ci.com/jmaggio14/imagepypelines
  :alt: build

.. image:: https://img.shields.io/pypi/l/imagepypelines.svg
  :target: https://badge.fury.io/py/imagepypelines

.. image:: https://codecov.io/gh/jmaggio14/imagepypelines/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/jmaggio14/imagepypelines
  :alt: coverage

.. image:: https://img.shields.io/pypi/pyversions/imagepypelines.svg
  :target: https://badge.fury.io/py/imagepypelines

.. image:: https://badge.fury.io/py/imagepypelines.svg
  :target: https://badge.fury.io/py/imagepypelines

.. image:: https://img.shields.io/pypi/status/imagepypelines.svg
  :target: https://badge.fury.io/py/imagepypelines

Imagepypelines is a package built by imaging scientists for imaging scientists.
It contains a simplistic front-end interface to construct complex image
processing pipelines, whilst automatically performing error checking,
task management and ultimately decreasing development time for many imaging
projects.

Imagepypelines is developed by alumni from RIT_'s `Imaging Science Program`_
who currently work in imaging related research or industries.

:raw-html:`<h5><i>This project is currently in alpha</i></h5>`



.. toctree:: installation.rst
    :maxdepth: 2

.. toctree:: about.rst
    :maxdepth: 2

.. toctree:: tutorials.rst
    :maxdepth: 2

.. toctree:: modules.rst
    :maxdepth: 2









What Makes Us Unique?
*********************

The Pipeline
^^^^^^^^^^^^
Imagepypelines_'s most powerful feature is a high level interface to create data processing pipelines which apply a sequence of algorithms to input data automatically.

In our experience as imaging scientists, processing pipelines in both corporate or academic settings are not always easy to adapt for new purposes and are therefore too often relegated to *proof-of-concept* applications only. Many custom pipelines may also not provide step-by-step error checking, which can make debugging a challenge.

.. image:: https://imgs.xkcd.com/comics/data_pipeline.png
  :alt: cracked pipelines
  :align: center


The **Pipeline** object of Imagepypelines_ allows for quick construction and prototyping, ensures end-to-end compatibility through each layer of a workflow, and leverages helpful in-house debugging utilities for use in image-centric or high-dimensional data routines.


The Block
^^^^^^^^^
Pipelines in Imagepypelines_ are constructed of processing `blocks` which apply an algorithm to a sequence of data passed into it.

.. image:: https://raw.githubusercontent.com/jmaggio14/imagepypelines/91b5f297632df16c2c246492782e37ea0a263b45/docs/images/pipeline-example.png


Each **block** *takes in* a list of data and *returns* a list of data, passing it onto the next block or out of the pipeline. This system ensures that blocks are compatible with algorithms that process data in batches or individually. Blocks also support label handling, and thus are **compatible with supervised machine learning systems or other algorithms that require training**

Broadly speaking, each box can be thought of as a black box which simply applies an operation to input data

.. image:: https://raw.githubusercontent.com/jmaggio14/imagepypelines/91b5f297632df16c2c246492782e37ea0a263b45/docs/images/block.png
    :align: center

a **datum** can be anything: an image array, a filename, a label -- pretty much any pythonic type.


Blocks can also output more or less datums than they take in and are thus capable of being used for culling or injecting data into the pipeline.

Hang on? are all blocks compatible with one another?
""""""""""""""""""""""""""""""""""""""""""""""""""""
not entirely, each block has predefined acceptable inputs and outputs. However the `Pipeline` object will validate the pipeline integrity before any data is processed


Building a pipeline
"""""""""""""""""""
building a pipeline is super easy

Image Display Pipeline
""""""""""""""""""""""

.. code-block:: python

  import imagepypelines as ip

  pipeline = ip.Pipeline(name='image display')
  pipeline.add( ip.ImageLoader() ) # each one of these elements are 'blocks'
  pipeline.add( ip.Resizer() )
  pipeline.add( ip.BlockViewer() )

  # now let's display some example data!
  pipeline.process( ip.standard_image_filenames() )

We just made a processing pipeline that can read in images, resize them and display them! but we can do much more complicated operations.

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

  pipeline = ip.Pipeline(blocks=[load,resize,fft,lowpass,ifft,display])

  # process a set of images (using imagepypelines' example data)
  filenames = ip.standard_image_filenames()
  pipeline.process(filenames)



Machine Learning Applications
"""""""""""""""""""""""""""""
One of the more powerful applications of Imagepypelines_ is it's ease of use in
*machine learning* and *feature engineering* applications.
we can easily tailor a pipeline to perform image classification

this classifier is available as a builtin Pipeline with fully tweakable hyperparameters as `ip.SimpleImageClassifier`

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


Processing Blocks built into imagepypeline
------------------------------------------
*more are being added with every commit!*

I/O operations
^^^^^^^^^^^^^^
- Image Display
- Camera Capture
- Image Loader
- Image Writing

Machine Learning
^^^^^^^^^^^^^^^^
- Linear Support Vector Machine
- Rbf Support Vector Machine
- Poly Support Vector Machine
- Sigmoid Support Vector Machine
- trainable neural networks
- 8 Pretrained Neural Networks (for feature extraction)
- Principle Component Analysis

Image Processing
^^^^^^^^^^^^^^^^
- colorspace conversion
- fast fourier transform
- frequency filtering
- Otsu Image Segmentation
- ORB keypoint and description
- Image resizing


Designing your own processing blocks
------------------------------------
There are two ways to create a block

1) quick block creation
^^^^^^^^^^^^^^^^^^^^^^^
for operations that can be completed in a single function that
accepts one datum, you can create a block with a single line.

.. code-block:: python

  import imagepypelines as ip

  # create the function we use to process images
  def normalize_image(img):
  	return img / img.max()

  # set up the block to work with grayscale and color imagery
  io_map = {ip.ArrayType([None,None]):ip.ArrayType([None,None]),
  			ip.ArrayType([None,None,3]):ipimagepypelines.ArrayType([None,None,3])}


  block = ip.quick_block(normalize_image, io_map)


2) object inheritance
^^^^^^^^^^^^^^^^^^^^^
*this is covered in more detail on our tutorial pages. this example will not cover training or label handling*

.. code-block:: python

  import imagepypelines as ip

  class NormalizeBlock(ip.SimpleBlock):
  	"""normalize block between 0 and max_count, inclusive"""
  	def __init__(self,max_count=1):
  		self.max_count = max_count
  		# set up the block to work with grayscale and color imagery
  		io_map = {ip.ArrayType([None,None]):ip.ArrayType([None,None]),
  					ip.ArrayType([None,None,3]):ip.ArrayType([None,None,3])}

  		super(NormalizeBlock,self).__init__(io_map)

  	def process(self,img):
  		"""overload the processing function for this block"""
  		return img.astype(np.float32) / img.max() * self.max_count
