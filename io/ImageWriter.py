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
import imsciutils as iu

@iu.experimental()
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

    input::
        output_dir (str):
            path to output directory that images will be saved to
        base_filename (str) = "image.png":
            filename common among all images, these will be incremented
            numerically as such
        size (tuple,None) = None:
            size of the image if forced resizing is desired, or
            None if raw write is desired
        interpolation (cv2 interpolation type) = cv2.INTER_NEAREST:
            interpolation method to be used if resizing is desired

    functions::
        write(frame):
            writes a frame with a unique filename to the specificed
            image directory
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
        input::
            frame (np.ndarray): frame to be saved to the output_dir
        return::
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
