"""
Helper functions that contain canned tests that we will run frequently
"""

import imsciutils



def interpolation_type_check(interp):
    """
    checks to see if the interpolation type is one of the acceptable
    values specified in opencv, otherwise raises an
    imsciutils.InvalidInterpolationType error
    """
    if interp not in imsciutils.CV2_INTERPOLATION_TYPES:
        raise imsciutils.InvalidInterpolationType(interp)

    return True
