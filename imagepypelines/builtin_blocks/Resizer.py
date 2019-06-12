# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018-2019 Jeff Maggio, Nathan Dileas, Ryan Hartzell
from .. import SimpleBlock
from .. import ArrayIn, ArrayOut
from ..core import import_opencv
cv2 = import_opencv()

class Resizer(SimpleBlock):
    def __init__(self,
                    to_height,
                    to_width,
                    interpolation=cv2.INTER_NEAREST):
        self.to_height = to_height
        self.to_width = to_width
        self.interpolation = interpolation

        to_shape2D = [self.to_height, self.to_width]
        to_shape3D = [self.to_height, self.to_width, 3]
        io_kernel = [
                    [ArrayIn(['N','M']),
                        ArrayOut(to_shape2D),
                        'Resizes a grayscale image to %s' % to_shape2D],
                    [ArrayType(['N','M',3]),
                        ArrayType(to_shape3D),
                        'Resizes a color image to %s' % to_shape3D],
                 ]

        super(Resizer,self).__init__(io_kernel, requires_training=False)

    def process(self,datum):
        resized = cv2.resize(datum,
                       dsize=(self.to_width,self.to_height),
                       interpolation=self.interpolation)
        return resized
