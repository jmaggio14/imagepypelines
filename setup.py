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
      include_package_data=True,
      install_requires=[
      'alabaster>=0.7.11',
      'Babel>=2.6.0',
      'certifi>=2018.8.24',
      'chardet>=3.0.4',
      'cloudpickle>=0.5.6',
      'colorama>=0.3.9',
      'CommonMark>=0.5.4',
      'cycler>=0.10.0',
      'dask>=0.19.2',
      'decorator>=4.3.0',
      'docutils>=0.14',
      'h5py>=2.8.0',
      'idna>=2.7',
      'imagesize>=1.1.0',
      'Jinja2>=2.10',
      'keras>=2.2.2',
      'keras-applications>=1.0.4',
      'keras-preprocessing>=1.0.2',
      'kiwisolver>=1.0.1',
      'm2r>=0.2.0',
      'MarkupSafe>=1.0',
      'matplotlib>=2.1.2',
      'mistune>=0.8.3',
      'networkx>=2.2',
      'numpy>=1.15.1',
      'opencv-python>=3.4.3.18',
      'packaging>=17.1',
      'Pillow>=5.2.0',
      'Pygments>=2.2.0',
      'pyparsing>=2.2.1',
      'python-dateutil>=2.7.3',
      'pytz>=2018.5',
      'PyWavelets>=1.0.0',
      'pyyaml>=4.2b4',
      'recommonmark>=0.4.0',
      'requests>=2.19.1',
      'scikit-image>=0.14.0',
      'scikit-learn>=0.20rc1',
      'scipy>=1.1.0',
      'six>=1.11.0',
      'snowballstemmer>=1.2.1',
      'Sphinx>=1.8.1',
      'sphinxcontrib-websupport>=1.1.0',
      'termcolor>=1.1.0',
      'toolz>=0.9.0',
      'urllib3>=1.23',
                        ],
      )
