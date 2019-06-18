#
# # context manager used for other tests down the line -- ignore
# import sys
# from contextlib import contextmanager
# from io import StringIO
#
#
# @contextmanager
# def Output():
#     new_out, new_err = StringIO(), StringIO()
#     old_out, old_err = sys.stdout, sys.stderr
#     try:
#         sys.stdout, sys.stderr = new_out, new_err
#         yield sys.stdout, sys.stderr
#     finally:
#         sys.stdout, sys.stderr = old_out, old_err
# # =================== color.py ===================
# # =================== debug.py ===================
# # =================== development_decorators.py ===================
# # =================== Summarizer.py ===================
#
# def test_Summarizer():
#     import imagepypelines as ip
#     import numpy as np
#     truth = "[ARRAY SUMMARY | shape: (512, 512) | size: 262144 | max: 1.0 | min: 0.0 | mean: 0.5 | dtype: float64]"
#
#     np.random.seed(0)
#     a = np.random.rand(512,512)
#     b = str( ip.util.summary(a) )
#     assert b == truth
# # =================== timing.py ===================
#
#
#
# class TestFunctionTimers(object):
#     def test_function_timer_ms(self):
#         import imagepypelines as ip
#         import time
#
#         @ip.util.function_timer_ms
#         def test_func():
#             time.sleep(.005)
#
#         # It isn't possible to reliably check the string printed to stdout
#         # to check timing accuracy
#         # here we just run the function to verify there are no easy errors
#         test_func()
#
#         # truth,dev = 1000, 2
#         # with Output() as (out,err):
#         #     test_func()
#         #     output = err.getvalue()
#         #
#         # output = output.replace("(  function_timer  )[    INFO    ] ran function 'test_func' in","")
#         # output = output[:-3]
#         #
#         # time_taken = float(output)
#         # assert (truth-dev) < time_taken and time_taken < (truth+dev)
#
#
#     def test_function_timer(self):
#         import imagepypelines as ip
#         import time
#
#         @ip.util.function_timer
#         def test_func():
#             time.sleep(.005)
#
#         test_func()
#         # truth,dev = 1, .002
#         # with Output() as (out,err):
#         #     test_func()
#         #     output = err.getvalue()
#         #
#         # output = output.replace("(  function_timer  )[    INFO    ] ran function 'test_func' in","")
#         # output = output[:-4]
#         #
#         # time_taken = float(output)
#         # assert (truth-dev) < time_taken and time_taken < (truth+dev)
