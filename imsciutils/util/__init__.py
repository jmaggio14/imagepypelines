# color.py
from .color import red
from .color import blue
from .color import green
from .color import yellow
from .color import magenta
from .color import cyan
from .color import color_text

# ConfigFactory.py
from .ConfigFactory import ConfigFactory

# error_checking.py
from .error_checking import interpolation_type_check
from .error_checking import dtype_type_check
from .error_checking import is_numpy_array
from .error_checking import is_iterable
from .error_checking import type_error_message

# format.py
from .format import format_dict

# permute.py
from .Permuter import Permuter

# timing.py
from .timing import Timer
from .timing import function_timer
from .timing import function_timer_ms

from .normalize import norm_01, norm_ab, norm_dtype