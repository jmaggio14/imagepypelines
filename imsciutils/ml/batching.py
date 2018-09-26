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
import cv2
from collections import Iterable
import numpy as np

from .. import core


def batches(data_list,batch_size):
    if batch_size > len(data_list):
        error_msg = "batch_size cannot be greater than the length of your dataset"
        core.error(error_msg)
        raise ValueError(error_msg)

    data_length = len(data_list)
    starts = list( range(0,data_length,batch_size) )
    ends = list( range(batch_size,data_length,batch_size) ) + [data_length]

    for start,end in zip(starts,ends):
        batch = data_list[start:end]
        yield batch

def load_and_stack_images(img_list):
    assert isinstance(img_list,Iterable),"img_list must be an iterable type"

    imgs = []
    for img in img_list:
        try:
            loaded = cv2.imread(img,cv2.IMREAD_UNCHANGED)
        except Exception as e:
            core.debug(e)
            core.error( "unable to open img: {}".format(img) )

        r,c,b,_ = core.dimensions(img)
        loaded = loaded.reshape( (1,r,c,b) )
        imgs.append(load)

    return np.vstack(imgs)
