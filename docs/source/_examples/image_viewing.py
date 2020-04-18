"""
Number and View Images
======================

Number and view a sequence of images
"""

###############################################################################

# Make sure we have the image plugin installed
import imagepypelines as ip
ip.require('image')

###############################################################################
# Define our tasks

tasks = {
        # set an entry point for images into the pipeline
        'images': ip.Input(),
        # add number to the bottom right corner
        'numbered': (ip.image.NumberImage(), 'images'),
        # View the numbered images in sequence
        'null' : (ip.image.QuickView(pause_for=500), 'numbered')
         }

viewer = ip.Pipeline(tasks)

###############################################################################
# Let's process some data!
# ------------------------
#

# First, let's grab some example data from the ImagePypelines standard set
images = [ip.image.panda(), ip.image.gecko(), ip.image.redhat()]
# Now number and view the images!
processed = viewer.process(images)
