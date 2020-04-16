"""
Number and View Images
======================

Number and view a sequence of images
"""

###############################################################################
import matplotlib.pyplot as plt
# make sure we have the image plugin
import imagepypelines as ip
ip.require('image')

###############################################################################

tasks = {
        # set an entry point for images into the pipeline
        'images': ip.Input(),
        # add number to the bottom left corner
        'numbered': (ip.image.NumberImage(), 'images'),
        # View the numbered images in sequence
        'null' : (ip.image.QuickView(pause_for=500), 'numbered')
         }

viewer = ip.Pipeline(tasks)

###############################################################################
# let's process some data!

# let's grab some example data
images = [ip.image.panda(), ip.image.gecko(), ip.image.redhat()]
# and then number and view the images!
processed = viewer.process(images)



###############################################################################
# This will display all numbered images in sequencegrab any processed data you need
# numbered_images = processed['numbered']
#
# plt.imshow(numbered_images[0])
# # To avoid matplotlib text output
# plt.show()
