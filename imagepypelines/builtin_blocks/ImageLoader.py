# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018-2019 Jeff Maggio, Nathan Dileas, Ryan Hartzell
# @Email:  jmaggio14@gmail.com
#
# MIT License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
#
# Copyright (c) 2018-2019 Jeff Maggio, Nathan Dileas, Ryan Hartzell
#
from .. import SimpleBlock
from .. import ArrayOut
from ..core import import_opencv
cv2 = import_opencv()


class ImageLoader(SimpleBlock):
    """Block to load in imagery from filenames
    Reads in an image using an input filename

    Args:
        None

    Attributes:

        io_map(IoMap): object that maps inputs to this block to outputs
        name(str): unique name for this block
        requires_training(bool): whether or not this block will require
            training
        trained(bool): whether or not this block has been trained, True
            by default if requires_training = False
        printer(ip.Printer): printer object for this block,
            registered to 'name'
    """
    def __init__(self):
        io_kernel = [
                    [str, ArrayOut([None, None]), "loads in a grayscale image from a filename"],
                    [str, ArrayOut([None, None, 3]), "loads in a color image from a filename"],
                    ]


        notes = "loads images from disk given an input filename"
        super(ImageLoader,self).__init__(io_kernel,
                                        notes=notes,
                                        requires_training=False)

    def process(self,datum):
        """loads in an image from a filename

        Args:
            datum (string): image filename

        Returns:
            image (np.ndarray): 2D or 3D array of image data
        """
        img = cv2.imread(datum)

        # throws error if unable to read img
        if img is None:
            error_msg = "unable to load {}".format(datum)
            self.printer.error(error_msg)
            raise FileNotFoundError(error_msg)

        return img
