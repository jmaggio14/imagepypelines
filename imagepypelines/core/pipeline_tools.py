# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018-2020 Jeff Maggio, Ryan Hartzell, and collaborators
#
from .block_subclasses import FuncBlock

################################################################################
def blockify(kwargs={},
                batch_size="each",
                types=None,
                shapes=None,
                containers=None):
    """decorator which converts a normal function into a un-trainable
    block which can be added to a pipeline. The function can still be used
    as normal after blockification (the __call__ method is setup such that
    unfettered access to the function is permitted)

    Args:
        **kwargs: hardcode keyword arguments for a function, these arguments
            will not have to be used to. defaults to {}
        types(:obj:`dict`,None): Dictionary of input types. If arg doesn't
            exist as a key, or if the value is None, then no checking is
            done. If not provided, then will default to args as keys, None
            as values.
        shapes(:obj:`dict`,None): Dictionary of input shapes. If arg doesn't
            exist as a key, or if the value is None, then no checking is
            done. If not provided, then will default to args as keys, None
            as values.
        containers(:obj:`dict`,None): Dictionary of input containers. If arg
            doesn't exist as a key, or if the value is None, then no
            checking is done. If not provided, then will default to args as
            keys, None as values.
            *if batch_size is "each", then the container is irrelevant and can
            be safely ignored!*
        batch_size(str, int): the size of the batch fed into your process
            function. Must be an integer, "all", or "each". defaults to Each

    Example:
        >>> import imagepypelines as ip
        >>>
        >>> @ip.blockify( kwargs=dict(value=10) )
        >>> def add_value(datum, value):
        ...    return datum + value
        >>>
        >>> type(add_value)
        <class 'FuncBlock'>



    """
    def _blockify(func):
        return FuncBlock(func,
                        kwargs,
                        batch_size=batch_size,
                        types=types,
                        shapes=shapes,
                        containers=containers)
    return _blockify
