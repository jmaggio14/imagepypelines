"""
Swap Red and Blue Image Channels
================================


"""
import numpy as np
import imagepypelines as ip
ip.require('image')
ip.set_log_level('debug')

###############################################################################


# swap red and blue color channels
@ip.blockify()
def swap_red_and_blue(image):
    return np.flip(image, axis=2)

###############################################################################
# Define our tasks and build the pipeline

tasks = {
        # set an entry point for images into the pipeline
        'images': ip.Input(),
        # swap channels
        'swapped': (swap_red_and_blue, 'images'),
        # Scale the images, cast dtype, and view the image comparisons!
        'safe': (ip.image.DisplaySafe(), 'swapped'),
        'null' : (ip.image.CompareView(pause_for=5000), 'images','safe')
         }

swap = ip.Pipeline(tasks)

###############################################################################
# Let's process some data!
# ------------------------
#
# Let's grab some example data from the ImagePypelines standard set
images = [ip.image.panda(), ip.image.gecko(), ip.image.redhat()]
# Number and view the images!
processed = swap.process(images)
