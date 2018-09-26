#
# @Email:  jmaggio14@gmail.com
#
# MIT License
#
# Copyright (c) 2018 Jeff Maggio, Nathan Dileas, Ryan Hartzell
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
import numpy as np
import cv2
from scipy.cluster.vq import kmeans, vq
from scipy.stats import wasserstein_distance as wd

class VBOW(object):
	"""Eventually this will inherit from the overarching FEATURE_VECTOR class"""

	def __init__(self, descriptors, descriptor_type='SIFT', sampling=4):

		self.step = float(1/sampling)
		self.descriptor_type = descriptor_type

		desc_norms = np.sum(descriptors, axis=1)/len(descriptors[0])
		self.desc_norms = np.asarray([[norm] for norm in desc_norms])
		
		codes = np.arange(0, 256, self.step)
		self.codes = np.asarray([[code] for code in codes])

		self.histogram = []

		del desc_norms
		del codes

		# MAKE VBOW SUMMARY VECTOR (FINGERPRINT)
		self.construct_vector()

	def construct_vector(self):
		"""For now, technically only supports SIFT (ORB needs special attention)"""
		idx, _ = vq(self.desc_norms, self.codes)
		
		for i in range(len(self.codes)):

			hist = len(self.desc_norms[idx==i])
			self.histogram.append(hist)
		
		return np.asarray(self.histogram)

def compare_euclidean(hist1, hist2):
	return np.sum(np.abs(np.asarray(hist2) - np.asarray(hist1)))

def compare_wasserstein(hist1, hist2):
	return wd(hist1, hist2)

if __name__ == '__main__':

	sift = cv2.xfeatures2d.SIFT_create()

	im1 = cv2.imread('../data/00001.png',0)
	kp, desc = sift.detectAndCompute(im1, None)

	VBOW1 = VBOW(desc)
	histogram1 =VBOW1.construct_vector()

	hist1sum = np.sum(histogram1)
	histogram1norm = histogram1/hist1sum

	print(histogram1norm)
	print(hist1sum)

	im2 = cv2.imread('../data/00102.png',0)
	kp2, desc2 = sift.detectAndCompute(im2, None)

	VBOW2 = VBOW(desc2)
	histogram2 = VBOW2.construct_vector()

	hist2sum = np.sum(histogram2)
	histogram2norm = histogram2/hist2sum

	print(histogram2norm)
	print(hist2sum)

	# diff_sum = np.sum(np.abs(np.asarray(histogram2) - np.asarray(histogram1)))
	# print(diff_sum)

	print('Here\'s the Earth Mover\'s Distance (Wasserstein):   ', compare_wasserstein(histogram1norm, histogram2norm)*100000)