from .. import SimpleBlock
from ..coordinates import dimensions
from ..filters import low_pass,high_pass
import numpy as np

class Highpass(SimpleBlock):
    """Block to apply a highpass filter to a Fourier transform

    Args:
        cut_off (float): cutoff frequency for this filter. units in #TODO
        filter_type (str): the type of filter to apply, 'ideal','gaussian',
            'butterworth'. default is 'ideal'
        butterworth_order(float): butterworth order if butterworth filter is
            being used. default is 1

    Attributes:
        cut_off (float): cutoff frequency for this filter. units in #TODO
        filter_type (str): the type of filter to apply, 'ideal','gaussian',
            'butterworth'
        butterworth_order(float): butterworth order if butterworth filter is
            being used
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
    def __init__(self,cut_off,filter_type='ideal',butterworth_order=1):
        self.cut_off = cut_off
        self.filter_type = filter_type
        self.butterworth_order = butterworth_order
        input_shape = [None,None],[None,None,None]
        output_shape = [None,None],[None,None,None]
        super(Highpass,self).__init__(input_shape=input_shape,
                                            output_shape=output_shape,
                                            requires_training=False)

    def process(self,datum):
        filter = high_pass(datum,
                    self.cut_off,
                    self.filter_type,
                    self.butterworth_order)

        if datum.ndim > 2:
            filter = np.dstack( [filter]*datum.shape[2] )

        return filter * datum



class Lowpass(SimpleBlock):
    """Block to apply a lowpass filter to a Fourier transform

    Args:
        cut_off (float): cutoff frequency for this filter. units in #TODO
        filter_type (str): the type of filter to apply, 'ideal','gaussian',
            'butterworth'. default is 'ideal'
        butterworth_order(float): butterworth order if butterworth filter is
            being used. default is 1

    Attributes:
        cut_off (float): cutoff frequency for this filter. units in #TODO
        filter_type (str): the type of filter to apply, 'ideal','gaussian',
            'butterworth'
        butterworth_order(float): butterworth order if butterworth filter is
            being used
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
    def __init__(self,cut_off,filter_type='ideal',butterworth_order=1):
        self.cut_off = cut_off
        self.filter_type = filter_type
        self.butterworth_order = butterworth_order
        input_shape = [None,None],[None,None,None]
        output_shape = [None,None],[None,None,None]
        super(Lowpass,self).__init__(input_shape=input_shape,
                                            output_shape=output_shape,
                                            requires_training=False)

    def process(self,datum):
        filter = low_pass(datum,
                    self.cut_off,
                    self.filter_type,
                    self.butterworth_order)

        if datum.ndim > 2:
            filter = np.dstack( [filter]*datum.shape[2] )

        return filter * datum
