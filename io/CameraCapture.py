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
import numpy as np
import time


class CameraCapture(object):
    """
    Payload child used to talk to pull imagery from UVC camera.

    Instantiation Args::
        cam (str,int) = 0:
            the file path to the camera, or alternatively the camera's
            numerical device id (on linux, this number is at the end of
            the camera's file path eg: "/dev/video0")

        fourcc (str) = "MJPG":
             the codec used to encode images off the camera. Many UVC
             camera device achieve highest frame rates with MJPG

    attributes::
        payload_name (str): an id for this camera. (can be retrieved
                from a marvin.quadcam.Frame retrieved from this payload)
        cap (cv2.VideoCapture): the cv2 camera object
        fourcc (str): the fourcc codec used for this camera
        frame_number (int): the number of frame retrieval attempts

    functions::
        retrieve
        get_status
        change_setting

    properties::

    """

    def __init__(self, cam=0, fourcc="MJPG"):
        assert isinstance(cam, (str, int)), "cam' must be str or int"
        assert isinstance(fourcc, str), "'fourcc' must be str"

        if isinstance(cam, str):
            if "/dev/video" in cam:
                cam = cam.replace("/dev/video", "")
            self.cam = int(cam)

        # openning the camera
        self.open()

        # setting the codec
        self.change_setting('fourcc', fourcc)
        self.__changeable_settings = {
            "width": cv2.CAP_PROP_FRAME_WIDTH,
            "height": cv2.CAP_PROP_FRAME_HEIGHT,
            "fps": cv2.CAP_PROP_FPS,
            "brightness": cv2.CAP_PROP_BRIGHTNESS,
            "contrast": cv2.CAP_PROP_CONTRAST,
            "hue": cv2.CAP_PROP_HUE,
            "gain": cv2.CAP_PROP_GAIN,
            "exposure": cv2.CAP_PROP_EXPOSURE,
            "foucc": cv2.CAP_PROP_FOURCC}

    def open():
        self.cap = cv2.VideoCapture(cam)
        self.frame_number = 0

    def retrieve(self):
        """
        reads an image from the capture stream, returns a static debug
        frame if it fails to read the frame

        input::
            None
        return::
            frame (marvin.Frame) image frame from the Capture Stream
            or debugging frame if there is a problem with the capture
        """
        status = False
        self.frame_number += 1
        self.current_frame_id = str(self.frame_number)

        if self.cap.isOpened():
            status, raw_frame = self.cap.read()
            metadata = self.get_status()

        elif not status or not self.cap.isOpened():
            debug_message = "unable to read frame {0}"\
                .format(self.current_frame_id)

            imgscitools.warning(debug_message)
            raise CameraReadError(debug_message)

        return frame, metadata

    def get_status(self):
        """
        grabs all metadata from the frame using the metadata properties
        and outputs it in an easy to use dictionary. also adds key
        "capture_time", which is the time.time() at the time the metadata
        is collected
        WARNING - what metadata is available is dependent on what
        camera is attached!

        input::
            None
        return::
            metadata (dict): dictionary containing all metadata values
        """
        metadata = {
            "width": self.__get_prop(cv2.CAP_PROP_FRAME_WIDTH),
            "height": self.__get_prop(cv2.CAP_PROP_FRAME_HEIGHT),
            "fps": self.__get_prop(cv2.CAP_PROP_FPS),
            "contrast": self.__get_prop(cv2.CAP_PROP_CONTRAST),
            "brightness": self.__get_prop(cv2.CAP_PROP_BRIGHTNESS),
            "hue": self.__get_prop(cv2.CAP_PROP_HUE),
            "gain": self.__get_prop(cv2.CAP_PROP_GAIN),
            "exposure": self.__get_prop(cv2.CAP_PROP_EXPOSURE),
            "writer_dims": (self.__get_prop(cv2.CAP_PROP_FRAME_HEIGHT),
                            self.__get_prop(cv2.CAP_PROP_FRAME_WIDTH)),
            "fourcc": self._fourcc,
            "fourcc_val": self.__get_prop(cv2.CAP_PROP_FOURCC),
            "capture_time": time.time(),
            "frame_number": self.current_frame_id
        }
        return metadata

    def change_setting(self, setting, value):
        """changes a setting on the capture object
        acceptable
        return::
            None
        """
        if setting in self.__changeable_settings.keys():
            flag = self.__changeable_settings[setting]
            if flag == "foucc":
                value = cv2.VideoWriter_fourcc(*value)
            ret = self.cap.set(flag, value)
            return ret
        else:
            raise ValueError("settings must be one of {0}"
                             .format(self.__changeable_settings.keys()))

    def __get_prop(self, flag):
        """
        gets a camera property
        wrapper for VideoCapture.get function

        input::
            flag (opencv constant): flag indicating what metadata to get

        return::
            the camera property requested
        """

        return self.cap.get(flag)

    def close(self):
        self.cap.release()
