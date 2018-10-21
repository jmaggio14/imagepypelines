#
# @Email:  jmaggio14@gmail.com
#
# MIT License: https://github.com/jmaggio14/imsciutils/blob/master/LICENSE
#
# Copyright (c) 2018 Jeff Maggio, Nathan Dileas, Ryan Hartzell
#
from .. import BatchBlock
from .. import ArrayType
from sklearn import svm


class LinearSVM(BatchBlock):
    """Linear support vector machine classifier
    """
    def __init__(self,C=1):
        self.C = C
        io_map = {ArrayType([1,None]):int}
        super(LinearSVM,self).__init__(io_map,
                                    requires_training=True,
                                    requires_labels=True)

    def train(self,train_data,train_labels):
        self.svc = svm.SVC(C=self.C,kernel='linear')
        train_data = np.vstack(train_data)
        self.svc.fit(train_data,train_labels)

    def batch_process(self,batch_data):
        # stacking input list into a numpy array
        stacked = np.vstack(batch_data)
        # predicting and returning a list of integers
        predictions = [int(lbl) for lbl in self.svc.predict(stacked)]
        return predictions
