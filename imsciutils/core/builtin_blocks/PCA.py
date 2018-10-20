
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
        # checking to make sure that enough components are specified
        if data.shape[1] < self.n_components:
            self.printer.warning("more components specified than features")
            self.printer.warning("truncating n_components({}) to num_features({})"\
                                    .format(self.n_components,data.shape[1]))
            # reinstantiating the class with fewer components
            # this is done to make sure that self.io_map is accurate
            self.__init__(data.shape[1],self.random_state)

        self.pca = PCA(self.n_components).fit(data)

    def batch_process(self,data):
        # stacking input data
        data = np.vstack(data)
        reduced = self.pca.transform(data)
        return np.vsplit(reduced,reduced.shape[0])
