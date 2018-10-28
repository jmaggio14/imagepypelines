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

# get list of installed packages, silence output
FNULL = open(os.devnull,'w')
reqs = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'],stderr=FNULL)
installed_packages = [r.decode().split('==')[0] for r in reqs.split()]
FNULL.close()

# import pdb; pdb.set_trace()

# check for tensorflow
if 'tensorflow' not in installed_packages:
    print("ERROR: tensorflow must be installed for imagepypelines to operate!")
    print("'pip install tensorflow --user' for CPU only")
    print("pip install tensorflow-gpu --user' for CPU+GPU")
    print("see README for details: https://github.com/jmaggio14/imagepypelines")
    sys.exit(1)
# check for opencv
if 'cv2' not in installed_packages:
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
del subprocess, sys, pkg_resources, os
