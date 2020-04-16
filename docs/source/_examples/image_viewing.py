"""
Number and View Images
======================

Number and view a sequence of images
"""

###############################################################################
# make sure we have the image plugin
import imagepypelines as ip
ip.require('image')

###############################################################################

tasks = {
        # set an entry point for images into the pipeline
        'images': ip.Input(),
        # add number to the bottom left corner
        'numbered': (ip.image.NumberImage(), 'images'),
        # View them!
        'null' : (ip.image.SequenceViewer(pause_for=500), 'numbered')
         }

viewer = ip.Pipeline(tasks)

###############################################################################
# let's grab some example data
images = [ip.image.panda(), ip.image.gecko(), ip.image.redhat()]
# and then number and view the images!
out = viewer.process(images)
