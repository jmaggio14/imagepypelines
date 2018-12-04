#!/usr/bin/env python

import os
from setuptools import setup, find_packages

# load __version__, __author__, __email__, etc variables
exec(open('imagepypelines/version_info.py').read())


with open('requirements.txt','r') as f:
    requirements = f.readlines()

long_description = ''
if os.path.exists('README.md'):
    with open('README.md', 'r') as f:
        long_description = f.read()

setup(name='imagepypelines',
      version=__version__,
      description=__description__,
      long_description=long_description,
      long_description_content_type='text/markdown',
      author=__author__,
      author_email=__email__,
      license=__license__,
      url=__url__,
      download_url=__download_url__,
      maintainer=__maintainer__,
      maintainer_email=__maintainer_email__,
      keywords=__keywords__,
      python_requires=__python_requires__,
      platforms=__platforms__,
      classifiers=__classifiers__,
      packages=find_packages(),
      include_package_data=True,
      install_requires=requirements,
      )

try:
    import tensorflow
except ImportError:
    print('\n\n')
    print("( imagepypelines ) WARNING: imagepypelines requires tensorflow to be installed separately!")
    print("( imagepypelines ) 'pip install tensorflow --user' for CPU only")
    print("( imagepypelines ) 'pip install tensorflow-gpu --user' for CPU+GPU")
    print("( imagepypelines ) see README for details: https://github.com/jmaggio14/imagepypelines")
    print('\n\n')

try:
    import cv2
except ImportError:
    print("( imagepypelines ) WARNING: imagepypelines requires opencv to be installed separately!")
    print("( imagepypelines ) see README for details: https://github.com/jmaggio14/imagepypelines")
