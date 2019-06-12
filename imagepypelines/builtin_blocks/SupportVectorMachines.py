# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018-2019 Jeff Maggio, Nathan Dileas, Ryan Hartzell
from .. import BatchBlock
from .. import ArrayIn
from sklearn import svm
import numpy as np


class SupportVectorMachine(BatchBlock):
    """general support vector machine classifier"""
    def __init__(self,kernel,C=1):
        assert kernel in ['linear', 'poly', 'rbf', 'sigmoid'],\
            "kernel must be one of ['linear', 'poly', 'rbf', 'sigmoid']"
        assert isinstance(C,(int,float)),"C must be a float or integer"

        self.kernel = kernel
        self.C = float(C)
        io_kernel = [[ArrayType([1,'N']),
                    int,
                    'predicts the classification label of the image based off of a feature vector']]
        super(SupportVectorMachine,self).__init__(io_kernel,
                                                    requires_training=True,
                                                    requires_labels=True)

    def train(self,train_data,train_labels):
        self.svc = svm.SVC(C=self.C,kernel=self.kernel)
        train_data = np.vstack(train_data)
        self.svc.fit(train_data,train_labels)

    def batch_process(self,batch_data):
        # stacking input list into a numpy array
        stacked = np.vstack(batch_data)
        # predicting and returning a list of integers
        predictions = [int(lbl) for lbl in self.svc.predict(stacked)]
        return predictions

class LinearSvm(SupportVectorMachine):
    def __init__(self,C=1):
        super(LinearSvm,self).__init__(kernel='linear',C=C)

class RbfSvm(SupportVectorMachine):
    def __init__(self,C=1):
        super(RbfSvm,self).__init__(kernel='rbf',C=C)

class PolySvm(SupportVectorMachine):
    def __init__(self,C=1):
        super(PolySvm,self).__init__(kernel='poly',C=C)

class SigmoidSvm(SupportVectorMachine):
    def __init__(self,C=1):
        super(SigmoidSvm,self).__init__(kernel='sigmoid',C=C)
