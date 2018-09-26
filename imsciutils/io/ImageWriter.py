#
# @Email:  jmaggio14@gmail.com
#
# MIT License
#
# Copyright (c) 2018 Jeff Maggio, Nathan Dileas, Ryan Hartzell
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
#
# marvin (c) by Jeffrey Maggio, Hunter Mellema, Joseph Bartelmo
#
# marvin is licensed under a
# Creative Commons Attribution-ShareAlike 4.0 International License.
#
# You should have received a copy of the license along with this
# work. If not, see <http://creativecommons.org/licenses/by-sa/4.0/>.
#
#

import cv2
from .. import core


@core.experimental()
class ImageWriter(object):
    """
    Class that operates as a system that saves single frames to a
    specified output directory.

    every new frame passed in will be saved in the following format:
        output_dir/000001example_filename.png
        output_dir/000002example_filename.png
        output_dir/000003example_filename.png
        ...

    automatic resizing is also available

    Args:
        output_dir (str):
            path to output directory that images will be saved to
        base_filename (str): default is 'image.png'
            filename common among all images, these will be incremented
            numerically with each new image saved
        size (tuple,None): Default is None
            size of the image if forced resizing is desired, or
            None if raw write is desired
        interpolation (cv2 interpolation type):
            Default is cv2.INTER_NEAREST
            interpolation method to be used if resizing is desired

    """

    def __init__(self, output_dir,
                         base_filename="image.png",
                         size=None,
                         interpolation=cv2.INTER_NEAREST):

        assert isinstance(base_filename, str), "'base_filename' must be str"
        imsciutils.util.interpolation_type_check(interpolation)

        self.base_filename = base_filename
        self.size = size
        self.interpolation = interpolation
        self.image_number = 0

    def write(self, frame):
        """
        writes an image frame to the specificed directory, forces
        resizing if specified when the class is instantiated

        Args:
            frame (np.ndarray): frame to be saved to the output_dir

        Returns:
            None
        """
        self.image_number += 1
        image_number = imsciutils.util.make_numbered_prefix(self.image_number,6)
        out_filename = os.path.join(self.output_dir,
                                    image_number + self.base_filename)

        if not isinstance(self.size, type(None)):
            frame = cv2.resize(frame,
                               dsize=(self.size[1], self.size[0]),
                               interpolation=self.interpolation)

        cv2.imwrite(filename, frame)
