
from sklearn.decomposition import PCA
from .. import BatchBlock
from .. import ArrayType
import numpy as np


class PCA(BatchBlock):
    def __init__(self,n_components,random_state=None):
        assert isinstance(n_components,(int,float)),\
            "n_components must be an integer"
        self.n_components = int(n_components)
        self.random_state

        io_map = {ArrayType([1,None]:ArrayType([1,self.n_components]))}
        super(PCA,self).__init__(io_map,
                                    requires_training=True,
                                    requires_labels=False,)

    def train(self,data,labels=None):
        # stacking input data
        data = np.vstack(data)
        self.pca = PCA(self.n_components).fit(data)

    def batch_process(self,data):
        # stacking input data
        data = np.vstack(data)
        processed = self.pca.transform(data)
        return np.vsplit(processed,processed.shape[0])
