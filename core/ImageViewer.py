import cv2
import numpy as np


class ImageViewer(object):
    """
    Class to simplify displaying images using opencv windows. Also has
    functionality to resize images automatically if desired

    On some systems (or opencv builds), openCV requires a waitkey to be
    called before displaying the image. This functionality is built in
    the view function with the argument 'force_waitkey'


    Instantian Args:
        window_name (str): the name of the window
        size (2 element tuple, None): (height, width) to resize image to
        interpolation (cv2 constant): cv2 interpolation flag for resizing
        enable_frame_counter (bool): whether or not to enable frame counter

    Attributes:
        window_name: name of the cv2 window
        size: size the images are being resized to
        interpolation: type of interpolation being usef for resizing
        enable_frame_counter: whether or not the frame counter is enabled
        frame_counter: index of the frame currently displayed

    """

    def __init__(self,
                 window_name,
                 size=None,
                 interpolation=cv2.INTER_NEAREST,
                 enable_frame_counter=False):
        self.window_name = str(window_name)
        self.size = size
        self.interpolation = interpolation
        self.enable_frame_counter = enable_frame_counter
        self.open()
        self.frame_counter = 1

    def open(self):
        """
        opens the image viewer, automatically called in __init__
        input::
            None
        return::
            None
        """
        cv2.namedWindow(self.window_name, cv2.WINDDW_AUTOSIZE)

    def view(self, frame, force_waitkey=True):
        """
        displays the frame passed into it, reopens itself if it
        input::
            frame (np.ndarray): image to be displayed
        return::
            force_waitkey (int) = 1:
                if greater than zero, then call a waitkey for the
                duration of the time given. this is required on some
                systems to display the image properly.
        """
        assert isinstance(frame, np.ndarray), "'frame' must be a numpy array"
        assert frame.ndim in [2, 3], "'frame' must be a 2D or 3D array"
        assert isinstance(force_waitkey, (int, float)),\
            "'force_waitkey' must be an integer"

        if isinstance(self.size, (tuple, list)):
            frame = cv2.resize(frame,
                               dsize=(self.size[1], self.size[0]),
                               interpolation=self.interpolation)

        # add a frame counter to an image thin
        if self.enable_frame_counter:
            frame = cv2.putText(frame,
                                text=str(self.frame_counter),
                                org=(0, 0),  # using bottem left origin
                                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                                fontScale=4,
                                color=(255, 255, 255),
                                thickness=2,
                                bottomLeftOrigin=True)

        # displaying the image
        cv2.imshow(self.window_name, frame)
        if force_waitkey:
            cv2.waitKey(force_waitkey)

        self.frame_counter += 1

    def enable_frame_counter(self):
        """enable the frame counter"""
        self.enable_frame_counter = True

    def disable_frame_counter(self):
        """disable the frame counter"""
        self.enable_frame_counter = False

    def close(self):
        """
        closes the image viewing window
        input::
            None
        return::
            None
        """
        cv2.destroyWindow(self.window_name)
