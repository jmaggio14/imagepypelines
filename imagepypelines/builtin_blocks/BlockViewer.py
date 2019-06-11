# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018-2019 Jeff Maggio, Nathan Dileas, Ryan Hartzell
from .. import SimpleBlock, ArrayIn, ArrayOut
from .. import Viewer
import time


class BlockViewer(SimpleBlock):
    """Block to view pipeline images,

    Views intermediate imagery in the block, the data is then passed unchanged
    to the next block

    Args:
        pause_time (int,float): time in seconds to pause after displaying
            the imagery. default is 0.1seconds
        enable_frame_counter(bool): whether or not to enable the viewer's
            frame counter. default is False

    Attributes:
        pause_time (int,float): time in seconds to pause after displaying
            the imagery. default is 0.1seconds

        io_map(IoMap): object that maps inputs to this block to outputs
        name(str): unique name for this block
        requires_training(bool): whether or not this block will require
            training
        trained(bool): whether or not this block has been trained, True
            by default if requires_training = False
        printer(ip.Printer): printer object for this block,
            registered to 'name'
    """

    def __init__(self,
                 pause_time=0.1,
                 FFT=False,
                 normalize=False,
                 enable_frame_counter=True):
        self.pause_time = pause_time
        io_kernel = [
                [ArrayIn['N','M'], ArrayOut['N','M'], "leave images unchanged"],
                [ArrayIn['N','M','3'], ArrayOut['N','M','3'], "leave images unchanged"],
                ]
        super(BlockViewer, self).__init__(io_kernel=,
                                          requires_training=False)
        self.viewer = Viewer(self.name, FFT=FFT, normalize=normalize)

    def process(self, datum):
        """displays the imagery in the image viewer

        Args:
            datum (np.ndarray): image to display

        Returns:
            datum(np.ndarray): the imagery displayed, unchanged
        """
        self.viewer.view(datum)
        time.sleep(self.pause_time)
        return datum

    def after_process(self):
        """closes the opencv window"""
        self.viewer.close()
