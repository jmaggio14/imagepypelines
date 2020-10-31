:orphan:

===============
Getting Started
===============

Installation
------------

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
                    <pre>pip install imagepypelines --user</pre>
                    <a class="copybtn o-tooltip--left" style="background-color: rgb(245, 245, 245)" data-tooltip="Copy" data-clipboard-target="#codecell0">
                      <img src="./_static/copy-button.svg" alt="Copy to clipboard">
                    </a>
                </div>
            </div>
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
        </div>
    </div>

Setting up a Virtual Environment
--------------------------------

If you have permissions-related installation issues, sometimes a virtual
environment can help

To set one up:

.. code-block:: shell

    python -m venv venv


And activate it with:

.. code-block:: shell

    venv/Scripts/activate


You should now be able to follow the installation steps above without issue. Deactivate your virtual environment with:

.. code-block:: shell

    deactivate



.. raw:: html

    <br><br>
