#
# @Email:  jmaggio14@gmail.com
#
# MIT License: https://github.com/jmaggio14/imsciutils/blob/master/LICENSE
#
# Copyright (c) 2018 Jeff Maggio, Nathan Dileas, Ryan Hartzell
#
from .. import SimpleBlock
from .. import ArrayType
import numpy as np

class IFFT(SimpleBlock):
    """Block to calculate an inverse fast fourier transform on input imagery

    Args:
        discard_imaginary (bool): whether or not to discard the imaginary output
            of the ifft. Default is True

    Attributes:
        discard_imaginary (bool): whether or not to discard the imaginary output
            of the ifft. Default is True
        input_shape(tuple): tuple of acceptable input shapes
        output_shape(tuple): tuple of acceptable output shapes
        name(str): unique name for this block
        requires_training(bool): whether or not this block will require
            training
        trained(bool): whether or not this block has been trained, True
            by default if requires_training = False
        printer(iu.Printer): printer object for this block,
            registered to 'name'

    """
    def __init__(self, discard_imaginary=True):
        self.discard_imaginary = discard_imaginary
        io_map = {ArrayType([None,None]):ArrayType([None,None]),
                    ArrayType([None,None,None]):ArrayType([None,None,None]),
                    }
        super(IFFT,self).__init__(io_map, requires_training=False)

    def process(self,datum):
        """calculates a fast-fourier transform on an input image

        Args:
            datum (np.ndarray): image numpy array to take fourier transform of

        Returns:
            fft(np.ndarray): zero-centered fourier transform

        """
        fft = np.fft.fftshift(datum)
        fft = np.fft.ifft2(datum)

        if self.discard_imaginary:
            fft = fft.real
        return fft
