"""
Image Filtering
===============
Learn how to filter images through a pipeline.
"""

###############################################################################

# Make sure we have the image plugin
import imagepypelines as ip
ip.require('image')

import numpy as np

###############################################################################

# Construct our filtering blocks

# FFT
@ip.blockify()
def fft(src):

    # Note: fft2d operates on LAST 2 axes of src (tensor-like: [Channels, W, H])
    return np.fft.fftshift(np.fft.fft2d(src)), src.shape

# IFFT
@ip.blockify()
def ifft(filtered):

    return np.fft.ifft2d(np.fft.fftshift(src))

# Frequency Filter
@ip.blockify()
def freq_filter(src, kernel):

    return src * kernel

# Circular Aperture
@ip.blockify()
def circ_aperture(shape): #, radius = 0.1):

    x, y = np.meshgrid(linspace(-1, 1, shape[0]), np.linspace(-1, 1, shape[1]))

    # For now, radius = 0.1, normalized to edge of the array
    radius = 0.1

    return (x - radius)*(x - radius) + (y - radius)*(y - radius)


###############################################################################
# Define our tasks

tasks = {
        # set an entry point for images into the pipeline
        'images': ip.Input(),
        # add number to the bottom right corner
        ('fft', 'shape'): (fft, 'images'),
        'circles': (circ_aperture, 'shape'),
        ('kernel', 'circ_shapes'): (fft, 'circles'),
        ('filtered'): (freq_filter, 'fft', 'kernel'),
        'ifft': (ifft, 'filtered'),
        # View the numbered images in sequence
        'null' : (ip.image.QuickView(pause_for=500), 'ifft')
         }

viewer = ip.Pipeline(tasks)

###############################################################################
# Let's process some data!
# ------------------------
#
# Let's grab some example data from the ImagePypelines standard set
images = [ip.image.panda(), ip.image.gecko(), ip.image.redhat()]
# Number and view the images!
processed = viewer.process(images)
