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


def centroid(img):
    """
    finds the centroid of the given image img
    input::
        img (np.ndarray):
            input img to find the centroid of
    return::
        centroid (tuple):
            centroid of the input image (height,width)
    """
    centroid = img.shape[0]//2, img.shape[1]//2
    return centroid


def frame_size(img):
    """
    return the height and width of a given img
    input::
        img (np.ndarray):
            input img to find frame_size of
    return::
        frame_size (tuple):
            height and width of the input img
    """
    frame_size = img.shape[0], img.shape[1]
    return frame_size


def dimensions(img,return_as_dict=False):
    """
    function which returns the dimensions and data_type of a given image

    input::
        img (np.ndarray):
            input image

    return::
        dimensions (tuple): of the form (rows, cols, bands, dtype)
    """
    rows = img.shape[0]
    cols = img.shape[1]
    if img.ndim == 3
        bands = img.shape[2]
    else:
        bands = 1
    dims = (rows, cols, bands, img.dtype)

    if return_as_dict:
        dims = dict(zip(('rows','cols','bands','dtype'), dims))

    return dims


# END
