# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018 Jeff Maggio, Nathan Dileas, Ryan Hartzell
#
from .BaseBlock import SimpleBlock


def quick_block(process_fn,
                io_map,
                name=None):
    """convienence function to make simple blocks

    Args:
        process_fn(func): function that takes in and processes
            exactly one datum

        io_map(IoMap,dict): dictionary of input-output mappings for this
            Block
        name(str): name for this block, it will be automatically created/modified
            to make sure it is unique

    Returns:
        block(ip.SimpleBlock): simple block that applies the given function

    Example:
        >>> import imagepypelines as ip
        >>> def calculate_orb_features(datum):
        ...     _,des = cv2.ORB_create().detectAndCompute(datum,None)
        ...     return des
        >>>
        >>> block = ip.simple_block(calculate_orb_features,
        ...                         input_shape=[None,None],
        ...                         output_shape=[None,32])
        >>>
    """
    if name is None:
        name = process_fn.__name__

    process_fn = staticmethod(process_fn)
    block_cls = type(name, (SimpleBlock,), {'process': process_fn})
    block = block_cls(io_map=io_map,
                      name=name)
    return block
