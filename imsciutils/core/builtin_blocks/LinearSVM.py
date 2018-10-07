from .. import BatchBlock
from sklearn import svm


class LinearSVM(BatchBlock):
    def __init__(self,C=1):
        self.C = C

        input_shape = [1,None]
        output_shape = int

        super(Resizer,self).__init__(input_shape=input_shape,
                                            output_shape=output_shape,
                                            requires_training=True)

    def train(self,train_data,train_labels):
        self.svc = svm.SVM(self.C)
        train_data = np.vstack(train_data)
        self.svc.fit(train_data,train_labels)

    def batch_process(self,batch_data):
        stacked = np.vstack(batch_data)
        predictions = self.svc.predict(stacked)
        predictions = np.vsplit(predictions,prediction.shape[0])
        return predictions
