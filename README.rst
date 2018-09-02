imsciutils
==========
This is a repo of code that we seem to find ourselves using in projects in many academic, personal, and corporate settings. It is not made for any specific purpose, and is meant to act in an accessory role to assist in odd imaging tasks.

We are imaging scientists, and as such the code in this repo will be skewed towards imaging tasks.

Compatibility
-------------
python 3.5 (python 2.7 backwards)

Module Dependencies
-------------------
- numpy
- matplotlib
- opencv
- scipy
- keras
- scikit-*

Documentation
-------------
There is autodoc sphinx documentation with this project, following the google docstrings format. To build / view these docs on windows::

	docs\make.bat html

And on every other platform::

	cd docs && make html

Then the html documentation will be available at docs/build/html/index.html
