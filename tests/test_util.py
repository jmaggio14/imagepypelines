
# context manager used for other tests down the line -- ignore
import sys
from contextlib import contextmanager
from io import StringIO


@contextmanager
def Output():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err
# =================== color.py ===================
# =================== debug.py ===================
# =================== development_decorators.py ===================
# =================== Summarizer.py ===================

def test_Summarizer():
    import imagepypelines as ip
    import numpy as np
    truth = "[ARRAY SUMMARY | shape: (512, 512) | size: 262144 | max: 1.0 | min: 0.0 | mean: 0.5 | dtype: float64]"

    np.random.seed(0)
    a = np.random.rand(512,512)
    b = str( ip.util.summary(a) )
    assert b == truth
# =================== timing.py ===================



class TestFunctionTimers(object):
    def test_function_timer_ms(self):
        import imagepypelines as ip
        import time

        @ip.util.function_timer_ms
        def test_func():
            time.sleep(1)

        with Output() as (out,err):
            test_func()
            print("stdout: this is a test")
            print("stderr: this is a test", file=err)
            output = err.getvalue()
            _err = err
            _out = out
        import pdb; pdb.set_trace()

if __name__ == "__main__":
    TestFunctionTimers().test_function_timer_ms()
