"""
Swap Red and Blue Image Channels
================================


"""

import imagepypelines as ip
ip.require('image')
ip.set_log_level('debug')

###############################################################################


# swap red and blue color channels
@ip.blockify()
def swap_red_and_blue(image):
    return np.flip(image, axis=2)
