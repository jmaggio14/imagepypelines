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
import marvin


def calculate_centroid(frame):
    """
    finds the centroid of the given image frame
    input::
        frame (np.ndarray):
            input frame to find the centroid of
    return::
        centroid (tuple):
            centroid of the input image (height,width)
    """
    centroid = frame.shape[0]//2,frame.shape[1]//2
    return centroid

def calculate_frame_size(frame):
    """
    return the height and width of a given frame
    input::
        frame (np.ndarray):
            input frame to find frame_size of
    return::
        frame_size (tuple):
            height and width of the input frame
    """
    frame_size = frame.shape[0],frame.shape[1]
    return frame_size

def get_image_dimensions(frame):
    """
    function which returns the dimensions and data_type of a given image

    input::
        frame (np.ndarray):
            input image

    return::
        dimensions (tuple): of the form (rows, cols, bands, dtype)
    """
    rows = frame.shape[0]
    cols = frame.shape[1]
    if len(frame.shape) == 3:
        bands = frame.shape[2]
    else:
        bands = 1
    dimensions = (rows, cols, bands, frame.dtype)
    return dimensions






#END
