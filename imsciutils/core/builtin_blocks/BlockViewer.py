from .. import SimpleBlock
from ..Viewer import Viewer
import time

class BlockViewer(SimpleBlock):
    def __init__(self,pause_time=0.1):
        self.pause_time = pause_time
        input_shape = [None,None],[None,None,3]
        output_shape = [None,None],[None,None,3]
        
        super(BlockViewer,self).__init__(input_shape,
                                        output_shape,
                                        requires_training=False)
        self.viewer = Viewer(self.name)

    def process(self,datum):
        self.viewer.view(datum)
        time.sleep(self.pause_time)
        return datum
