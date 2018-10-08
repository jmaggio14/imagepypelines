from .. import SimpleBlock
from ..Viewer import Viewer
import time

class BlockViewer(SimpleBlock):
    """Block to view pipeline images,

    Views intermediate imagery in the block, the data is then passed unchanged
    to the next block

    Args:
        pause_time (int,float): time in seconds to pause after displaying
            the imagery. default is 0.1seconds
    """
    def __init__(self,pause_time=0.1):
        self.pause_time = pause_time
        input_shape = [None,None],[None,None,3]
        output_shape = [None,None],[None,None,3]

        super(BlockViewer,self).__init__(input_shape,
                                        output_shape,
                                        requires_training=False)
        self.viewer = Viewer(self.name)

    def process(self,datum):
        """displays the imagery in the image viewer

        Args:
            datum (np.ndarray): image to display

        Returns:
            datum(np.ndarray): the imagery displayed, unchanged
        """
        self.viewer.view(datum)
        time.sleep(self.pause_time)
        return datum
