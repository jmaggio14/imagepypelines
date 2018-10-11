#
# @Email:  jmaggio14@gmail.com
#
# MIT License: https://github.com/jmaggio14/imsciutils/blob/master/LICENSE
#
# Copyright (c) 2018 Jeff Maggio, Nathan Dileas, Ryan Hartzell
#
from ... import util
from .. import BatchBlock
from random import shuffle



class MnistLoader(BatchBlock):
    def __init__(self,should_shuffle=False):
        self.should_shuffle = should_shuffle
        self.images = []
        self.image_labels = []
        io_map = {str:ArrayType([None,None])}
        super(MnistLoader,self).__init__(io_map,requires_training=False)

    def before_process(self,data,labels=None):
        assert data[0] in ['train','test']

        from keras.datasets import mnist

        if data[0] == 'train':
            x_data, y_data = mnist.load_data()[0]
        elif data[0] == 'test':
            x_data, y_data = mnist.load_data()[1]

        images = [np.squeeze(x_data[i,:,:]) for i in range(x_data.shape[0])]
        image_labels = [int(lbl) for lbl in y_data]

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
