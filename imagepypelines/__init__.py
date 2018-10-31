# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018 Jeff Maggio, Nathan Dileas, Ryan Hartzell

# check if the dependencies that aren't included in the setup.py are installed
import subprocess
import sys
import os

tf_names = ['tensorflow','tensorflow-gpu']
cv2_names = ['cv2','opencv-python']

# get list of installed packages, silence output
try:
    FNULL = open(os.devnull,'w')
    reqs = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'],stderr=FNULL)
    installed_packages = [r.decode().split('==')[0] for r in reqs.split()]

    has_tf = any(name in installed_packages for name in tf_names)
    has_cv2 = any(name in installed_packages for name in cv2_names)

    del reqs
    del installed_packages
    # if this raises a processError, then we can't access pip for some reason
    # so we'll simply attempt imports the slow way
except subprocess.CalledProcessError:
    has_tf = False
    has_cv2 = False
finally:
    FNULL.close()


# check for tensorflow
if not has_tf:
    # try an import just in case it was installed in a way pip doesn't recognize
    ## this will be much slower, which is why it isn't done natively
    try:
        import tensorflow as tf
        del tf
    except ImportError as e:
        print("ERROR: tensorflow must be installed for imagepypelines to operate!")
        print("'pip install tensorflow --user' for CPU only")
        print("'pip install tensorflow-gpu --user' for CPU+GPU")
        print("see README for details: https://github.com/jmaggio14/imagepypelines")
        sys.exit(1)

# check for opencv
if not has_cv2:
    # try an import just in case it was installed in a way pip doesn't recognize
    ## this will be much slower, which is why it isn't done natively
    ## for opencv, this will be any source build
    try:
        import cv2
        del cv2
    except ImportError as e:
        print("ERROR: opencv must be installed for imagepypelines to operate!")
        print("see README for details: https://github.com/jmaggio14/imagepypelines")
        sys.exit(1)




import pkg_resources
STANDARD_IMAGE_DIRECTORY = pkg_resources.resource_filename(__name__,
                                                        'data/standard_images')


from .version_info import *
from .core import *
from . import util
from . import ml
from . import io

# delete namespace pollutants
del subprocess, sys, pkg_resources, os,
del FNULL, tf_names, has_tf, cv2_names, has_cv2
