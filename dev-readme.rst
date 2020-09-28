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


How to run tests
----------------

*in top-level project directory*
.. code-block:: console

   py.test --verbose


**with code coverage tracking**
.. code-block:: console

   py.test --cov=./imagepypelines --ignore=setup.py --verbose


How to build docker images
--------------------------




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
