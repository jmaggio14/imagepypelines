#
# @Email:  jmaggio14@gmail.com
#
# MIT License: https://github.com/jmaggio14/imsciutils/blob/master/LICENSE
#
# Copyright (c) 2018 Jeff Maggio, Nathan Dileas, Ryan Hartzell
#
from ... import util
from .. import BatchBlock
from .. import ArrayType
from random import shuffle
import numpy as np



class MnistLoader(BatchBlock):
    def __init__(self,should_shuffle=False):
        self.should_shuffle = should_shuffle
        self.images = []
        self.image_labels = []
        io_map = {str:ArrayType([None,None])}
        super(MnistLoader,self).__init__(io_map,requires_training=False)


    def train(self,data,labels=None):
        from keras.datasets import mnist
        # loading train data from mnist
        x_train, y_train = mnist.load_data()[0]

        images = [np.squeeze(x_train[i,:,:]) for i in range(x_train.shape[0])]
        image_labels = [int(lbl) for lbl in y_train]

        if self.should_shuffle:
            combined = list(zip(images, image_labels))
            shuffle(combined)
            images[:], image_labels[:] = zip(*combined)

        return images, image_labels

    def before_process(self,data,labels=None):
        from keras.datasets import mnist
        # loading test data from mnist
        x_test, y_test = mnist.load_data()[1]

        images = [np.squeeze(x_test[i,:,:]) for i in range(x_test.shape[0])]
        image_labels = [int(lbl) for lbl in y_test]

        if self.should_shuffle:
            combined = list(zip(images, image_labels))
            shuffle(combined)
            images[:], image_labels[:] = zip(*combined)

        self.images = images
        self.image_labels = image_labels

    def batch_process(self,data):
        # JM: return image list created in before_process
        return self.images

    def labels(self,labels):
        # JM: return label list created in before_process
        return self.image_labels


    def after_process(self):
        # JM: reset these values to empty lists to reduce idle memory footprint
        self.images = []
        self.image_labels = []
