======================
Installation and Setup
======================

- `The Imagepypelines Shell`_
- `Installation`_
    * `via pip`_
    * `dependencies`_
        + `tensorflow`_
        + `opencv`_

**Python compatibility:** 3.4-3.6 | 64bit

Installation
************

**via pip**
^^^^^^^^^^^

.. code-block:: shell

  pip install imagepypelines --user

**dependencies**
^^^^^^^^^^^^^^^^

when running natively, imagepypelines requires *opencv* and *tensorflow* to be installed
on your machine

**tensorflow**
""""""""""""""

.. code-block:: shell

    pip install tensorflow --user
    # OR if you have a GPU
    # pip install tensorflow-gpu --user

**opencv**
""""""""""

we **strongly recommend** that you `build opencv from source`_. However unofficial bindings for Opencv can be installed with

.. code-block:: shell

  pip install opencv-python --user

*(while we haven't encountered many problems with these unofficial bindings,
they will likely not be as optimized and we do not guarantee support)*

.. _build opencv from source: https://docs.opencv.org/3.4/df/d65/tutorial_table_of_content_introduction.html


The Imagepypelines shell
************************
`imagepypelines` provides `docker images`_ (virtual environments) which contain
all the libraries and tools you'll need to develop and run imagepypeline's code

1) Simply `install Docker`_
2) type :code:`imagepypelines shell` into your terminal!

.. _docker images: https://hub.docker.com/r/imagepypelines/imagepypelines-tools
.. _install Docker: https://docs.docker.com

You be will launched into a virtual environment that is guaranteed to work
hassle-free without installing your dependencies.

.. image:: https://raw.githubusercontent.com/jmaggio14/imagepypelines/12d3c4d7dd2b04f0dbf38eb1ae84d532aa226cdf/docs/images/imagepypelines-shell.png
    :alt: Imagepypelines Shell
