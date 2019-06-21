
======================
Convenience functions
======================

`ImagePypelines` contains convenience functions and utilities meant to
accelerate working with imagery and machine learning



.. contents:: Convenience Utilities
  :depth: 3

.. ============================================================================
..                                 IMAGERY
.. ============================================================================

Imagery
-------

.. ----------------------- Standard Imagery -----------------------
Standard Imagery
~~~~~~~~~~~~~~~~

.. ----- lenna
lenna
*******

**description**
"""""""""""""""
`ImagePypelines` contains helper functions to quickly retrieve imagery that are
frequently used as benchmarks in the Imaging Science community

**Example**
"""""""""""
.. doctest:: python

    >>> import imagepypelines as ip
    >>> lenna = ip.lenna()
    >>> linear_gradient = ip.linear()
    >>> giza = ip.giza()
    >>> panda = ip.panda()

A full list of standard images can be retrieved with `ip.list_standard_images()`

for those of you in the Imaging Science program at RIT, there are a couple
easter eggs for ya ;)

.. doctest:: python

    >>> import imagepypelines as ip
    >>> ip.quick_image_view( ip.carlenna() )
    >>> ip.quick_image_view( ip.roger() )
    >>> ip.quick_image_view( ip.pig() )

.. ----------------------- Viewing Imagery -----------------------
Viewing Imagery
~~~~~~~~~~~~~~~

.. ----- Viewer
Viewer
*******

**description**
"""""""""""""""
Video Viewer

**Example**
"""""""""""
.. doctest:: python

  >>> import imagepypelines as ip
  >>> import time
  >>>
  >>> viewer = ip.Viewer('example_name')
  >>> # display all standard images in sequence
  >>> for img in ip.standard_image_gen():
  ...   viewer.view(img)
  ...   time.sleep(.1)
  >>>


.. ----- quick_image_view
quick_image_view
****************

**description**
"""""""""""""""
To display a single image in its own window

**Example**
"""""""""""
.. doctest:: python

  >>> import imagepypelines as ip
  >>> lenna = ip.lenna()
  >>>
  >>> ip.quick_image_view(lenna)
  >>> # this next line will normalize and bin the image first
  >>> ip.quick_image_view(lenna, True)


.. ----------------------- Image Coordinates -----------------------
Image Coordinates
~~~~~~~~~~~~~~~~~

.. ----- dimensions
dimensions
****************

**description**
"""""""""""""""
Get quick coordinates and dimensions for imagery. Mostly useful to clean up
code and avoid silly mistakes

**Example**
"""""""""""
.. doctest:: python

  >>> import imagepypelines as ip
  >>> lenna = ip.lenna()
  >>>
  >>> # center pixel in the image
  >>> center_row, center_col = ip.centroid(lenna)
  >>>
  >>> # number of rows and columns
  >>> rows, cols = ip.frame_size(lenna)
  >>>
  >>> # shape and dtype
  >>> rows, cols, bands = ip.dimensions(lenna)


.. ----------------------- Normalization and Binning Imagery -----------------------
Normalization and Binning Imagery
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. ----- display_safe
normalization to various ranges
*******************************

**description**
"""""""""""""""
Forgetting to make imagery normalized or display_safe gets you more often
than you think...

**Example**
"""""""""""
.. doctest:: python

  >>> import imagepypelines as ip
  >>> import numpy as np
  >>>
  >>> random_pattern = np.random.rand(512, 512).astype(np.float32)
  >>> lenna = ip.lenna()
  >>>
  >>> # normalize [0,255] and cast to uint8 for display
  >>> display_safe = ip.display_safe(random_pattern)
  >>>
  >>> # normalize lenna to [0,1] inclusive
  >>> lenna_0_1 = ip.norm_01( lenna )
  >>> # normalize lenna to [a,b] inclusive
  >>> lenna_100_255 = ip.norm_ab(lenna, 100, 255)
  >>> # normalize to the whole 16bit range
  >>> lenna_16bit = ip.norm_dtype(lenna, np.uint16)


.. =============================================================================
..                                 MACHINE LEARNING
.. =============================================================================

Machine Learning
----------------

.. ----------------------- Machine Learning Metrics -----------------------
Metrics
~~~~~~~

.. ----- accuracy
accuracy
********

**description**
"""""""""""""""
*this is a description of what I do*

**Example**
"""""""""""
.. doctest:: python

  >>> # <code>


.. ----- confidence
confidence
**********

**description**
"""""""""""""""
*this is a description of what I do*

**Example**
"""""""""""
.. doctest:: python

  >>> # <code>



.. ----------------------- Dataset Management -----------------------
Dataset Management
~~~~~~~~~~~~~~~~~~

.. ----- DatasetManager
DatasetManager
*****************

**description**
"""""""""""""""
*this is a description of what I do*

**Example**
"""""""""""
.. doctest:: python

  >>> # <code>

.. ----- Mnist
Mnist
*****************

**description**
"""""""""""""""
*this is a description of what I do*

**Example**
"""""""""""
.. doctest:: python

  >>> # <code>


.. ----- MnistFashion
MnistFashion
*****************

**description**
"""""""""""""""
*this is a description of what I do*

**Example**
"""""""""""
.. doctest:: python

  >>> # <code>


.. ----- Cifar10
Cifar10
*****************

**description**
"""""""""""""""
*this is a description of what I do*

**Example**
"""""""""""
.. doctest:: python

  >>> # <code>


.. ----- Cifar100
Cifar100
*****************

**description**
"""""""""""""""
*this is a description of what I do*

**Example**
"""""""""""
.. doctest:: python

  >>> # <code>

.. =============================================================================
..                                 Development Tools
.. =============================================================================
====

Development Tools
-----------------



TODO
--------
- caching
- constants that may be useful?
- error_checking?
- filters
- everything in io currently
- Printing
- quick types
- image writing
- video writing
- camera capture
- output.py
- color text
- Summarization
