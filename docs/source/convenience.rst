
======================
Convenience functions
======================

`ImagePypelines` contains convenience functions and utilities meant to
accelerate working with imagery and machine learning



.. contents:: Convenience Utilities
  :depth: 3

*Topic*
-------

*Subset*
~~~~~~~

*Name*
******

**description**
"""""""""""""""
*this is a description of what I do*

**Example**
"""""""""""
.. code-block:: python

  >>> <code>
.. ============================================================================
..                                 IMAGERY
.. ============================================================================
====

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
.. code-block:: python

    >>> import imagepypeplines as ip
    >>> lenna = ip.lenna()
    >>> linear_gradient = ip.linear()
    >>> giza = ip.giza()
    >>> panda = ip.panda()

A full list of standard images can be retrieved with `list_standard_images()`

.. code-block:: python

    >>> import imagepypelines as ip
    >>> ip.quick_image_view( ip.carlenna() )
    >>> ip.quick_image_view( ip.roger() )
    >>> ip.quick_image_view( ip.pig() )


*---- all other std images and functions here here ----*

.. ----------------------- Viewing Imagery -----------------------
Viewing Imagery
~~~~~~~~~~~~~~~

.. ----- Viewer
Viewer
*******

**description**
"""""""""""""""
*this is a description of what I do*

**Example**
"""""""""""
.. code-block:: python

  >>> <code>


.. ----- quick_image_view
quick_image_view
****************

**description**
"""""""""""""""
*this is a description of what I do*

**Example**
"""""""""""
.. code-block:: python

  >>> <code>


.. ----------------------- Image Coordinates -----------------------
Image Coordinates
~~~~~~~~~~~~~~~~~

.. ----- centroid
centroid
****************

**description**
"""""""""""""""
*this is a description of what I do*

**Example**
"""""""""""
.. code-block:: python

  >>> <code>


.. ----- frame_size
frame_size
****************

**description**
"""""""""""""""
*this is a description of what I do*

**Example**
"""""""""""
.. code-block:: python

  >>> <code>


.. ----- dimensions
dimensions
****************

**description**
"""""""""""""""
*this is a description of what I do*

**Example**
"""""""""""
.. code-block:: python

  >>> <code>



.. ----------------------- Normalization and Binning Imagery -----------------------
Normalization and Binning Imagery
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. ----- normalize_and_bin
normalize_and_bin
*****************

**description**
"""""""""""""""
*this is a description of what I do*

**Example**
"""""""""""
.. code-block:: python

  >>> <code>


.. ----- norm_01
norm_01
****************

**description**
"""""""""""""""
*this is a description of what I do*

**Example**
"""""""""""
.. code-block:: python

  >>> <code>


.. ----- norm_ab
norm_ab
****************

**description**
"""""""""""""""
*this is a description of what I do*

**Example**
"""""""""""
.. code-block:: python

  >>> <code>


.. ----- norm_dtype
norm_dtype
****************

**description**
"""""""""""""""
*this is a description of what I do*

**Example**
"""""""""""
.. code-block:: python

  >>> <code>

.. =============================================================================
..                                 MACHINE LEARNING
.. =============================================================================
====

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
.. code-block:: python

  >>> <code>


.. ----- confidence
confidence
**********

**description**
"""""""""""""""
*this is a description of what I do*

**Example**
"""""""""""
.. code-block:: python

  >>> <code>



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
.. code-block:: python

  >>> <code>

.. ----- Mnist
Mnist
*****************

**description**
"""""""""""""""
*this is a description of what I do*

**Example**
"""""""""""
.. code-block:: python

  >>> <code>


.. ----- MnistFashion
MnistFashion
*****************

**description**
"""""""""""""""
*this is a description of what I do*

**Example**
"""""""""""
.. code-block:: python

  >>> <code>


.. ----- Cifar10
Cifar10
*****************

**description**
"""""""""""""""
*this is a description of what I do*

**Example**
"""""""""""
.. code-block:: python

  >>> <code>


.. ----- Cifar100
Cifar100
*****************

**description**
"""""""""""""""
*this is a description of what I do*

**Example**
"""""""""""
.. code-block:: python

  >>> <code>

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
