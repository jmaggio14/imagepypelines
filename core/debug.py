import os
import sys
import traceback
import imsciutils as iu

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

	iu.error(error_msg)