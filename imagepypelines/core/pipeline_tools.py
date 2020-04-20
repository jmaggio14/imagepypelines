# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018-2020 Jeff Maggio, Ryan Hartzell, and collaborators
#
from .block_subclasses import FuncBlock

################################################################################
def blockify(global_ns, kwargs={},
                batch_type="each",
                types=None,
                shapes=None,
                containers=None,
                void=False):
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
            *if batch_type is "each", then the container is irrelevant and can
            be safely ignored!*
        batch_type(str, int): the type of the batch processing for your
            process function. Either "all" or "each". `all` means that all
            argument data will be passed into to your function at once,
            `each` means that each argument datum will be passed in
            individually
        void(bool): Boolean value. By default all blocks return a value or
            values as output. However, if printing to screen, plotting, or
            saving data to a file, a block may not have a meaningful output
            that should be stored in a pipeline's output dictionary. In this
            case, void should be set to True, so that the output of the block
            is ignored. The associated var key in the pipeline output will
            contain a value of :obj:`None`.

    Example:
        >>> import imagepypelines as ip
        >>>
        >>> @ip.blockify(globals(), kwargs=dict(value=10) )
        >>> def add_value(datum, value):
        ...    return datum + value
        >>>
        >>> type(add_value)
        <class 'FuncBlock'>



    """
    def _blockify(func):
        return FuncBlock(func,
                        global_ns,
                        kwargs,
                        batch_type=batch_type,
                        types=types,
                        shapes=shapes,
                        containers=containers,
                        void=void)
    return _blockify
