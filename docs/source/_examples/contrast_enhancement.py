"""
Re-reimplement histogram stretching, matching, and equalization and hist/pdf/cdf
================================================================================

1) Require ip.image
2) Build image histogram, PDF, and CDF blocks
2) Build LUT application block
4) Build a contrast enhancement block
5) Display comparison of original vs equalized

* We should definitely have a more robust block for doing these with pooling too

NOTE: AMONG US ($5 on steam)
"""

###############################################################################
# First let's import our basic libraries
import numpy as np
import matplotlib.pyplot as plt
import imagepypelines as ip
ip.require('image')

###############################################################################
# We'll also need to set up a few blocks

# A block for computing the histogram, pdf, and cdf of an image
@ip.blockify()
def compute_stats(image, bit_depth=8):
    hist, bins = np.histogram(image, bins=np.linspace(0, (2**bit_depth)+1, (2**bit_depth)+1))
    pdf = hist / image.size
    cdf = np.cumsum(pdf)
    return hist, pdf, cdf

# A quick block for building a histogram equalization look-up table (LUT)
@ip.blockify()
def equalization_LUT(image_cdf, bit_depth=8):
    target_cdf = np.cumsum(np.ones(2**bit_depth) / 2**bit_depth)
    lut = np.searchsorted(target_cdf, image_cdf)
    return lut

# A quick block for applying a LUT to an image
@ip.blockify()
def apply_LUT(image, lut):
    return lut[image].astype(image.dtype)

# A quick block for plotting original versus stretched histograms
@ip.blockify(batch_type="each", void=True)
def compare_stats(original, equalized):
    fig = plt.figure()
    plt.plot(np.linspace(0,len(original)-1,len(original)), original, color='r')
    plt.plot(np.linspace(0,len(equalized)-1,len(equalized)), equalized, color='b')
    plt.ion()
    plt.show()

# stats = compute_stats(ip.image.giza())
# eq_stats = compute_stats(apply_LUT(ip.image.giza(), equalization_LUT(stats[2])))
# compare_stats(stats[0], eq_stats[0])

tasks = {
        # set an entry point for images into the pipeline
        'images': ip.Input(),
        # compute image stats
        ('hists', 'pdfs', 'cdfs'): (compute_stats, 'images'),
        # construct equalization LUT
        'LUTs': (equalization_LUT, 'cdfs'),
        # apply LUT
        'applied': (apply_LUT, 'images', 'LUTs'),
        # Scale the images, cast dtype, and view the stretched images
        # in sequence!
        'safe': (ip.image.DisplaySafe(), 'applied'),
        'viewing' : (ip.image.CompareView(pause_for=1000), 'images','safe'),
        # show graph of hist (red) and eq_hist (blue),
        ('eq_hists', 'eq_pdfs', 'eq_cdfs'): (compute_stats, 'applied'),
        'plotted': (compare_stats, 'hists', 'eq_hists')
        }

# Pipeline setup
contrast = ip.Pipeline(tasks)

# Let's grab some example data from the ImagePypelines standard set
images = [ip.image.giza(), ip.image.crowd()]

# And let's see some results!
contrast(images)
