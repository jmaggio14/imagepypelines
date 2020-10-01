How to add licenses to our files (required for our CI to deploy to pypi)
------------------------------------------------------

*in top-level project directory*

.. code-block:: shell

   python enforcer.py --modify

.. _____________________________________________________________________________

How to build website locally
----------------------------

*on Linux/OSX*
*in imagepypelines/docs*

.. code-block:: shell

   make html

*on Windows*
*in imagepypelines/docs*

.. code-block:: shell

   .\make.bat html

.. _____________________________________________________________________________


How to build angular template files
-----------------------------------

1. Install NodeJS 12.X.X

*in imagepypelines-tools/ip-client*

.. code-block:: shell

    npm i && ng build:prod

.. _____________________________________________________________________________

How to run tests
----------------

*in top-level project directory*

.. code-block:: console

   py.test --verbose


**with code coverage tracking**

.. code-block:: console

   py.test --cov=./imagepypelines --ignore=setup.py --verbose

.. _____________________________________________________________________________

How to build/run dashboard docker image
---------------------------------------

1. Build the image

.. code-block:: shell

    cd imagepypelines-tools\imagepypelines_tools\dockerfiles
    docker build --tag dashboard -f .\dashboard.Dockerfile .


2. Run the image

.. code-block:: shell

   docker run --rm -p 5000:5000 -p 9000:9000 dashboard:latest



How to push to pypi manually
----------------------------

1. Install Dependencies

.. code-block:: shell

   pip install wheel twine


2. Create Distributions


.. code-block:: shell

   python setup.py sdist bdist_wheel


3. (optional) Upload to testpypi

(to verify things worked)


.. code-block:: shell

   twine upload -r testpypi -u <pypi username> -p <pypi pass> dist/*



4. Upload to pypi

.. code-block:: shell

  twine upload -u <pypi username> -p <pypi pass> dist/*
