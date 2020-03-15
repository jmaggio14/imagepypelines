# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018-2020 Jeff Maggio, Nathan Dileas, Ryan Hartzell



class PipelineError(RuntimeError):
    """Error raised within a Pipeline"""
    pass


class BlockError(RuntimeError):
    """Error raised within a Block"""
    pass


class InputTypeError(RuntimeError):
    """Error raised if the wrong type is passed in"""
    pass
