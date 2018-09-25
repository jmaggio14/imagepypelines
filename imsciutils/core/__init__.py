#
# @Email:  jmaggio14@gmail.com
#
# MIT License
#
# Copyright (c) 2018 Jeff Maggio, Nathan Dileas, Ryan Hartzell
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# constants.py
from .constants import *

# coordinates.py
from .coordinates import centroid
from .coordinates import frame_size
from .coordinates import dimensions

# debug.py
from .debug import debug

# development_decorators.py
from .development_decorators import deprecated
from .development_decorators import experimental
from .development_decorators import human_test
from .development_decorators import print_args
from .development_decorators import unit_test

# Exceptions
from .Exceptions import CameraReadError
from .Exceptions import InvalidInterpolationType
from .Exceptions import InvalidNumpyType

# Printer.py
from .Printer import get_printer
from .Printer import whitelist_printer
from .Printer import blacklist_printer
from .Printer import reset_printer_lists
from .Printer import Printer
from .Printer import disable_printout_colors
from .Printer import enable_printout_colors
from .Printer import get_active_printers
from .Printer import set_global_printout_level

# printout.py
from .printout import get_default_printer
from .printout import debug
from .printout import info
from .printout import warning
from .printout import error
from .printout import critical
from .printout import comment


# standard_image.py
from .standard_image import list_standard_images
from .standard_image import standard_image_gen
from .standard_image import get_standard_image
from .standard_image import standard_image_input

# ND 9/7/18 - dynamically load each of the previously created convience funcs
# into the current namespace
from .standard_image import STANDARD_IMAGES
from .standard_image import funcs
import sys

curr_module = sys.modules[__name__]
for img_name in STANDARD_IMAGES.keys():
	setattr(curr_module, img_name, getattr(funcs, img_name))

# ND 9/7/18 - delete these so that the imsciutils namespace is not polluted
del sys, curr_module, funcs, STANDARD_IMAGES

# Viewer.py
from .Viewer import Viewer

# img_tools.py
from .img_tools import normalize_and_bin
from .img_tools import quick_image_view
from .img_tools import number_image



# Tester.py
from .Tester import Tester

# Summarizer.py
from .Summarizer import Summarizer
