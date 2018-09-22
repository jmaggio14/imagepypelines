#!/usr/bin/env python

import os
from setuptools import setup, find_packages

# load __version__, __author__, __email__, etc variables
exec(open('imsciutils/version_info.py').read())

long_description = ''
if os.path.exists('README.md'):
    with open('README.md', 'r') as f:
        long_description = f.read()

setup(name='imsciutils',
      version=__version__,
      description='Convienence library to accelerate the development of imaging science projects',
      long_description=long_description,
      long_description_content_type='text/markdown',
      author=__author__,
      author_email=__email__,
      license=__license__,
      url=__url__,
      keywords='imaging science machine learning computer vision',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Topic :: Scientific/Engineering'
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python',
          # 'Programming Language :: Python :: 2.7', # JM: currently the code is 3.5+ only
          # 'Programming Language :: Python :: 3.3',
          # 'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Natural Language :: English',
          ],
      packages=find_packages(),
      install_requires=['numpy',
                        'scipy',
                        'matplotlib',
                        'keras',
                        'scikit-learn',
                        'colorama',
                        'termcolor',
                        'opencv3',
                        'Pillow',
                        ],
      )
