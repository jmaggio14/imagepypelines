# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018 - 2020 Jeff Maggio, Jai Mehra, Ryan Hartzell



class PipelineError(RuntimeError):
    """Error raised within a Pipeline"""
    pass


class BlockError(RuntimeError):
    """Error raised within a Block"""
    pass


class DashboardWarning(RuntimeWarning):
    """Warning for connection failure to dashboard"""
    pass
