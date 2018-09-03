import os
import sys
import traceback
import imsciutils as iu

def debug(exception):
	"""
	simple method to remove unecessary clutter in debugging
	meant to be called exclusively in a try statement
	simply prints the file,line and exeption has occured in more organized
	and easily readable fashion
	"""
	exc_type, exc_obj, tb = sys.exc_info()
	fname = os.path.split(tb.tb_frame.f_code.co_filename)[1]
	line = tb.tb_lineno
	traceback.print_tb(tb)
	print("\r\n")
	iu.error("===============================================================")
	iu.error("                   | initital traceback | ")
	iu.error("file: {0}\r\n\r\nline: {1} \r\n\r\ntype: {2}\r\n\r\n{3}\r\n"\
                                        .format(fname,line,exc_type,exception))
	iu.error("===============================================================")
