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
import os
import sys
import traceback
from .printout import error as iuerror

def debug(exception):
	"""
	simple method to remove unecessary clutter in debugging
	meant to be called exclusively in a except statement
	simply prints the file, line and exeption has occured in more organized
	and easily readable fashion
	"""
	exc_type, exc_obj, tb = sys.exc_info()
	fname = os.path.basename(tb.tb_frame.f_code.co_filename)
	line = tb.tb_lineno
	traceback.print_tb(tb)
	print("\r\n")
	error_msg = \
	"""
	===============================================================
						| initital traceback |
	file: {fname}

	line: {line}

	type: {exc_type}

	{exception}
	===============================================================
	""".format(fname=fname,
				line=line,
				exc_type=exc_type,
				exception=exception)

	iuerror(error_msg)
