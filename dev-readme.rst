How to add licenses to our files (required for our CI to deploy to pypi)
------------------------------------------------------

*in top-level project directory*
.. code-block:: shell

   python enforcer.py --modify


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


How to build angular template files
-----------------------------------

1. Install NodeJS 12.X.X

*in imagepypelines-tools/ip-client*

.. code-block:: shell

    npm i && ng build:prod


How to run tests
----------------

*in top-level project directory*
.. code-block:: console

   py.test --verbose


**with code coverage tracking**
.. code-block:: console

   py.test --cov=./imagepypelines --ignore=setup.py --verbose


How to build/run dashboard docker image
---------------------------------------

manually with docker
********************

Build the image
###############

```bash
cd imagepypelines-tools\imagepypelines_tools\dockerfiles
docker build --tag dashboard -f .\dashboard.Dockerfile .
```

Run the image
#############
```bash
docker run --rm -p 5000:5000 -p 9000:9000 dashboard:latest
```


How to push to pypi manually
----------------------------

Install Dependencies
********************

.. code-block:: shell

   pip install wheel twine


Create Distrobutions
********************

.. code-block:: shell

   python setup.py sdist bdist_wheel


Upload to testpypi
******************

to verify things worked


.. code-block:: shell

   twine upload -r testpypi -u <pypi username> -p <pypi pass> dist/*



Upload to pipy
******************

to verify things worked


.. code-block:: shell

  twine upload -r testpypi -u <pypi username> -p <pypi pass> dist/*
