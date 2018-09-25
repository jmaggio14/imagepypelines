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
import termcolor
import os

# enabling colorama's ANSI code switcher if system is using windows
# so colored printouts will work
if os.name == 'nt':
    import colorama
    colorama.init()


COLOR_CODES = {
    "r": "red",    "red": "red",
    "g": "green",  "green": "green",
    "y": "yellow", "yellow": "yellow",
    "b": "blue",   "blue": "blue",
    "m": "magenta", "magenta": "magenta",
    "c": "cyan",   "cyan": "cyan",
    "w": "white",  "white": "white",
    None: None
}

BACKGROUND_CODES = {
    "r": "on_red",    "red": "on_red",
    "g": "on_green",  "green": "on_green",
    "y": "on_yellow", "yellow": "on_yellow",
    "b": "on_blue",   "blue": "on_blue",
    "m": "on_magenta", "magenta": "on_magenta",
    "c": "on_cyan",   "cyan": "on_cyan",
    "w": "on_white",  "white": "on_white",
    None: None
}

def red(text, bold=False):
    """adds ansi codes to text so it appears to be red when printed"""
    if bold:
        return color_text(text, color='red', attrs=['bold'])
    return color_text(text, color='red')


def blue(text, bold=False):
    """adds ansi codes to text so it appears to be blue when printed"""
    if bold:
        return color_text(text, color='blue', attrs=['bold'])
    return color_text(text, color='blue')


def green(text, bold=False):
    """adds ansi codes to text so it appears to be green when printed"""
    if bold:
        return color_text(text, color='green', attrs=['bold'])
    return color_text(text, color='green')


def yellow(text, bold=False):
    """adds ansi codes to text so it appears to be yellow when printed"""
    if bold:
        return color_text(text, color='yellow', attrs=['bold'])
    return color_text(text, color='yellow')

def magenta(text, bold=False):
    """adds ansi codes to text so it appears to be magenta when printed"""
    if bold:
        return color_text(text, color='magenta', attrs=['bold'])
    return color_text(text, color='magenta')

def cyan(text, bold=False):
    """adds ansi codes to text so it appears to be cyan when printed"""
    if bold:
        return color_text(text, color='cyan', attrs=['bold'])
    return color_text(text, color='cyan')



def color_text(text, color="r", background=None, attrs=None):
    """
    adds ansi escape codes to a string to change the color in a terminal
    printout
    using print(color_text_output) with with windows powershell or
    cmd prompt will not yield a colored string
    example::
        >>> warning_msg = color_text('this is a warning',
        ...                                color = 'red',
        ...                                background = 'yellow',
        ...                                attrs = ['bold','underline'])
        >>> warning_msg
        '\x1b[4m\x1b[1m\x1b[43m\x1b[31mthis is a warning\x1b[0m'
    input::
        text (str):
            Input text to colorize
        color (str) = 'r':
                String which indicates the color to use for the text
                acceptable values are:
                                "r",    "red",
                                "g",  "green",
                                "y", "yellow",
                                "b",   "blue",
                                "m", magenta",
                                "c",   "cyan",
                                "w",  "white",
        background (str) = None:
                String which indicates what color to use for the text's
                background colors.
                acceptable values are:
                                "r",    "red",
                                "g",  "green",
                                "y", "yellow",
                                "b",   "blue",
                                "m", magenta",
                                "c",   "cyan",
                                "w",  "white",
        attrs (list) = None:
                additional styles that can be applied to the text. This
                must be a list or tuple
                acceptable values are:
                                "bold",
                                "dark",
                                "underline",
                                "reverse",
                                "concealed"
    return::
        colored_text (str):
                string with proper color codes added (colored string)
    """
    assert isinstance(text, str), "'text' must be a string"
    assert isinstance(color, str), "color' must be a string"
    assert isinstance(color, str), "background' must be a string"
    assert isinstance(attrs, (type(None), list, tuple)),\
        "'attrs must be a list,tuple,NoneType'"

    if attrs == None:
        attrs = []

    out_attrs = []
    if "bold" in attrs:
        out_attrs.append("bold")
    if "dark" in attrs:
        out_attrs.append("dark")
    if "underline" in attrs:
        out_attrs.append("underline")
    if "reverse" in attrs:
        out_attrs.append("reverse")
    if "concealed" in attrs:
        out_attrs.append("concealed")
    if out_attrs == []:
        out_attrs = None

    #
    if color in COLOR_CODES.keys() and background in BACKGROUND_CODES.keys():
        text_color = COLOR_CODES[color]
        text_background = BACKGROUND_CODES[background]

    else:
        error_msg = "invalid color or background code must be one of {all} \
                                        \ncolor input: {color_input} \
                                        \nbackground input: {background_input}"\
                                        .format(all=list(COLOR_CODES.keys()),
                                                color_input=color,
                                                background_input=background)
        raise ValueError(error_msg)

    colored_text = termcolor.colored(text,
                                     color=text_color,
                                     on_color=text_background,
                                     attrs=out_attrs)
    return colored_text
