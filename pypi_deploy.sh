#!/bin/bash
# THESE COMMANDS WILL ONLY WORK IF YOU HAVE A PROPERLY CONFIGURED ~/.pypirc FILE
# contact Jeff Maggio if you need to set this up

# trap the error code in a variable so we can check error_status
err=0
trap 'err=1' ERR

# remove existing dists if they exist
DIRECTORY="dist/"
if [ -d "$DIRECTORY" ]; then
  rm dist/*
fi

# setup a virtual environment
pip install pipenv
pipenv shell

# create the necessary dists using setup.py
# this will put the wheel and source in dist/
python setup.py sdist bdist_wheel

# ensure twine is installed
pip install twine

# install dependencies that aren't included in requirements.txt
pip install opencv-python tensorflow==1.10.0

# upload to testpypi to check
twine upload --repository testpypi dist/*

# attempt an install from testpypi
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple imagepypelines

# attempt a python import
python -c "import imagepypelines as ip"

# if no error occurs then push to the real pypi
if [ ! err ]; then
  twine upload dist/*
fi
