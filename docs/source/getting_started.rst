:orphan:

.. _opencv-python: https://pypi.org/project/opencv-python/

.. include:: isoamsa.txt

===============
Getting Started
===============

The `imagepypelines` package is a pipeline processing library for scientists who
want to make their code more scalable and sharable with their colleagues.
**It’s designed with scientists in mind, not software engineers.**

.. It’s designed with scientists in mind, not software engineers.
.. Scientific simplicity over software complexity

ImagePypelines contains tools to turn scripts into robust processing pipelines
which can be visualized, saved, copied, or deployed to a server easily.

Installation
************

.. Add badges for version, build, etc
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
  :alt: python versions

.. image:: https://badge.fury.io/py/imagepypelines.svg
  :target: https://badge.fury.io/py/imagepypelines
  :alt: pypi package

.. image:: https://img.shields.io/pypi/status/imagepypelines.svg
  :target: https://badge.fury.io/py/imagepypelines
  :alt: status

.. raw:: html

    <br><br>

.. raw:: html

    <ul class="nav nav-pills">
        <li class="active">
            <a data-toggle="pill" href="#pip">Pip</a>
        </li>
        <li>
            <a data-toggle="pill" href="#conda">Conda</a>
        </li>
        <li>
            <a data-toggle="pill" href="#source">From Source</a>
        </li>
    </ul>
    <!-- PILL CONTENT -->
    <div class="tab-content">
        <div id="pip" class="tab-pane active fade in active"><br>
            ImagePypelines is python3 only, so this might be "pip3" on your machine :p<br>
            <i>(remove <code>--user</code> to install systemwide)</i>
            <div class='highlight-shell notranslate'>
                <div class='highlight'>
                    <pre>pip install imagepypelines[all] --user</pre>
                    <a class="copybtn o-tooltip--left" style="background-color: rgb(245, 245, 245)" data-tooltip="Copy" data-clipboard-target="#codecell0">
                      <img src="./_static/copy-button.svg" alt="Copy to clipboard">
                    </a>
                </div>
            </div>
            <br/>
            **Note: remove the <code>[all]</code> if you don't wish to install default plugins or <a href='https://pypi.org/project/opencv-python/'>opencv-python</a>.
        </div>
        <div id="conda" class="tab-pane fade"><br>
            <div class='highlight-shell notranslate'>
                <div class='highlight'>
                    <pre>coming soon!</pre>
                    <a class="copybtn o-tooltip--left" style="background-color: rgb(245, 245, 245)" data-tooltip="Copy" data-clipboard-target="#codecell0">
                      <img src="./_static/copy-button.svg" alt="Copy to clipboard">
                    </a>
                </div>
            </div>
        </div>
        <div id="source" class="tab-pane fade"><br>
            ImagePypelines is python3 only, so this might be "python3" on your machine :p
            <div class='highlight-shell notranslate'>
                <div class='highlight'>
                    <pre>git clone https://www.github.com/jmaggio14/imagepypelines.git<br>cd imagepypelines<br>python setup.py install</pre>
                    <a class="copybtn o-tooltip--left" style="background-color: rgb(245, 245, 245)" data-tooltip="Copy" data-clipboard-target="#codecell0">
                      <img src="./_static/copy-button.svg" alt="Copy to clipboard">
                    </a>
                </div>
            </div>
            <br/>
            **Note: This will not install the official ImagePypelines plugins. See the <b>Advanced Startup</b> section below to manually install the Image and Astro plugins.
        </div>

    </div>

.. raw:: html

    <br/>


ImagePypelines Makes Your Scripts More Powerful
***********************************************


**placeholder until my capstone code is done**

.. table::
    :widths: auto
    :align: center

    +-------------------------------------+----------------------------------------------------+
    |        Without ImagePypelines       |                 With ImagePypelines                |
    +=====================================+====================================================+
    | .. code-block:: python              | .. code-block:: python                             |
    |                                     |                                                    |
    |     import numpy as np              |     import numpy as np                             |
    |                                     |     import imagepypelines as ip                    |
    |                                     |                                                    |
    |     # let's build a linear function |     # let's build a linear function                |
    |     def y(m,x,b):                   |     @ip.blockify()                                 |
    |         return m*x + b              |     def y(m,x,b):                                  |
    |                                     |         return m*x + b                             |
    |                                     |                                                    |
    |     m = np.ones(500) * 5            |     m = np.ones(500) * 5                           |
    |     x = np.arange(500)              |     x = np.arange(500)                             |
    |     b = np.ones(500) * 12           |     b = np.ones(500) * 12                          |
    |                                     |                                                    |
    |     y = y(m,x,b)                    |     tasks = {                                      |
    |                                     |             # inputs                               |
    |                                     |             'm' : ip.Input(0),                     |
    |                                     |             'x' : ip.Input(1),                     |
    |                                     |             'b' : ip.Input(2),                     |
    |                                     |             # linear transformer                   |
    |                                     |             'y' : (y, 'm','x','b'),                |
    |                                     |             }                                      |
    |                                     |     pipeline = ip.Pipeline(tasks)                  |
    |                                     |                                                    |
    |                                     |     y = pipeline.process_and_grab(m,x,b,fetch='y') |
    +-------------------------------------+----------------------------------------------------+
    |    *I'm a boring normal script*     |    *I can be saved to disk, deployed to a server,* |
    |                                     |               *or monitored remotely!*             |
    +-------------------------------------+----------------------------------------------------+


.. .. code-block:: python
..
..     import imagepypelines as ip
..     import numpy as np
..
..     # let's build a linear function
..     @ip.blockify()
..     def y(m,x,b):
..         return m*x + b
..
..     m = np.ones(500) * 5
..     x = np.arange(500)
..     b = np.ones(500) * 12
..
..     tasks = {
..             # inputs
..             'm' : ip.Input(0),
..             'x' : ip.Input(1),
..             'b' : ip.Input(2),
..             # linear transformer
..             'y' : (y, 'm','x','b'),
..             }
..     pipeline = ip.Pipeline(tasks)
..
..     y = pipeline.process_and_grab(m,x,b,fetch='y')


..
.. .. code-block:: python
..
..     import numpy as np
..
..
..     # let's build a linear function
..     def y(m,x,b):
..         return m*x + b
..
..
..     m = np.ones(500) * 5
..     x = np.arange(500)
..     b = np.ones(500) * 12
..
..     y = m*x + b



Using the Dashboard
-------------------
**<include video here>**


.. raw:: html

    <br/>


------------

Advanced
********

Setting up a Virtual Environment
--------------------------------

If you have permissions-related installation issues, sometimes a virtual
environment can help

To set one up:

.. code-block:: shell

    python -m venv venv


And activate it with:

.. code-block:: shell

    # Windows
    venv/Scripts/activate

    # Linux
    venv/bin/activate


You should now be able to follow the installation steps above without issue. Deactivate your virtual environment with:

.. code-block:: shell

    deactivate


Configuring Your ImagePypelines Installation
--------------------------------------------


--------

Image Plugin
############

ImagePypelines requires OpenCV bindings
by default for use in the official `image <https://www.github.com/jmaggio14/imagepypelines_image>`_ plugin.
If you do not have a local OpenCV installation compiled from source, you may install opencv-python_
on your system or in a virtual environment alongside imagepypelines. Careful though! opencv-python_
WILL overwrite your own local OpenCV bindings, so proceed with caution!

*without opencv*

.. code-block:: shell

    pip install imagepypelines_image

*with opencv*

.. code-block:: shell

    pip install imagepypelines_image[cv]


--------

Astro Plugin
############


Likewise, install our official `astronomy <https://www.github.com/jmaggio14/imagepypelines_astro>`_ plugin via

*this is installed by default with imagepypelines[all]*

.. code-block:: shell

    pip install imagepypelines_astro

--------

Backends
########

Brief overview of our various messaging, dashboard, and runtime backends.
Currently not a very long list and should reflect vanilla IP. As example redis vs current TCP implementation for messaging


Testing
--------

You may want to verify your installation by running the hello-world test pipeline:

.. code-block:: shell

    imagepypelines hello-world

    # Output: Hello World!

If your output matches then you're ready to code! See our `Examples <examples/index.html>`_ for help converting your script.


ImagePypelines Command Line Interface Overview
----------------------------------------------

More in depth than above. Go over all commands in great detail with example use cases


For Developers
--------------

All the developer centric goodies relating to ImagePypelines. Installation, Contribution Guidelines, etc

Installing Docker
-----------------

While not required, installing `Docker <https://docs.docker.com/get-docker/>`_
will make it easier to run our Dashboard.

You can invoke this containerized version with

:code:``


.. raw:: html

    <br><br>
