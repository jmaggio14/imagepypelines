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
import marvin
from marvin.payload import Payload
import numpy as np
import time

class CameraCapture(Payload):
    """
    Payload child used to talk to pull imagery from UVC camera.
    Payload name is "Camera"+str(cam)

    Instantiation Args::
        cam (str,int) = 0:
            the file path to the camera, or alternatively the camera's
            numerical device id (on linux, this number is at the end of
            the camera's file path eg: "/dev/video0")

        fourcc (str) = "MJPG":
             the codec used to encode images off the camera. Many UVC
             camera device achieve highest frame rates with MJPG

        payload_name (str) = None:
            The name for this payload. This will be used as a unique
            identifier for the camera and will become part of any
            frame_id generated for a Frame from this camera

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
    def __init__(self,cam=0,fourcc="MJPG"):
        assert isinstance(cam,(str,int)),"cam' must be str or int"
        assert isinstance(fourcc,str),"'fourcc' must be str"

        if isinstance(cam,str):
            if "/dev/video" in cam:
                cam = cam.replace("/dev/video","")
            cam = int( cam )


        self.payload_name = str( cam )
        self.cap = cv2.VideoCapture( cam )
        # setting the codec
        self.change_setting('fourcc',fourcc)
        self.__changeable_settings = {
                                "width":cv2.CAP_PROP_FRAME_WIDTH,
                                "height":cv2.CAP_PROP_FRAME_HEIGHT,
                                "fps":cv2.CAP_PROP_FPS,
                                "brightness":cv2.CAP_PROP_BRIGHTNESS,
                                "contrast":cv2.CAP_PROP_CONTRAST,
                                "hue":cv2.CAP_PROP_HUE,
                                "gain":cv2.CAP_PROP_GAIN,
                                "exposure":cv2.CAP_PROP_EXPOSURE,
                                "foucc":cv2.CAP_PROP_FOURCC}
        self.frame_number = 0
        super(CameraCapture,self).__init__(
                                payload_name="Camera"+self.payload_name)

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
        self.current_frame_id = self.__create_frame_id(self.payload_name,
                                                        self.frame_number)
        if self.cap.isOpened():
            metadata = self.get_status()
            status,raw_frame = self.cap.read()
            if status:
                frame = marvin.Frame(raw_frame,self.current_frame_id,metadata)

        if not status or not self.cap.isOpened():
            debug_message = "unable to read frame {0} from camera {1}"\
                                    .format(self.current_frame_id,payload_name)
            # frame = marvin.DebugImage(message=debug_message,
            #                             frame_id=self.current_frame_id)
            frame = self.__debug_frame()

        return frame

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
            "width":self.__get_prop(cv2.CAP_PROP_FRAME_WIDTH),
            "height":self.__get_prop(cv2.CAP_PROP_FRAME_HEIGHT),
            "fps":self.__get_prop(cv2.CAP_PROP_FPS),
            "contrast":self.__get_prop(cv2.CAP_PROP_CONTRAST),
            "brightness":self.__get_prop(cv2.CAP_PROP_BRIGHTNESS),
            "hue":self.__get_prop(cv2.CAP_PROP_HUE),
            "gain":self.__get_prop(cv2.CAP_PROP_GAIN),
            "exposure":self.__get_prop(cv2.CAP_PROP_EXPOSURE),
            "writer_dims":(self.__get_prop(cv2.CAP_PROP_FRAME_HEIGHT),
                            self.__get_prop(cv2.CAP_PROP_FRAME_WIDTH)),
            "fourcc":self._fourcc,
            "fourcc_val":self.__get_prop(cv2.CAP_PROP_FOURCC),
            "capture_time":time.time(),
            "frame_id":self.current_frame_id
            }
        return metadata

    def change_setting(self,setting,value):
        """changes a setting on the capture object
        acceptable
        return::
            None
        """
        if setting in self.__changeable_settings.keys():
            flag = self.__changeable_settings[setting]
            if flag == "foucc":
                value = cv2.VideoWriter_fourcc(*value)
            ret = self.cap.set(flag,value)
            return ret
        else:
            raise ValueError("settings must be one of {0}"
                        .format(self.__changeable_settings.keys()))



    def __get_prop(self,flag):
        """
        gets a camera property
        wrapper for VideoCapture.get function

        input::
            flag (opencv constant): flag indicating what metadata to get

        return::
            the camera property requested
        """

        return self.cap.get(flag)

    def __debug_frame(self):
        """
        builds a static debug frame containing debug text

        input::
            None

        return::
            frame (np.ndarray): debug frame
        """
        metadata = self.get_status()
        h,w = metadata["height"],metadata["width"]
        if isinstance(h,type(None)) or isinstance(w,type(None)):
            h,w = 256,256

        frame = np.zeros( (h,w), dtype=np.uint8 )
        centroid = marvin.centroid(frame)
        frame = cv2.putText(frame,
                            "error reading frame{0}".format(self.frame_number),
                            centroid,
                            cv2.FONT_HERSHEY_SIMPLEX,
                            5,
                            (255,255))
        return frame


    def __create_frame_id(self,payload_name,frame_number):
        """
        creates a frame_id from the camera id and the frame number
        by casting the inputs to a string
        frame_id is the in the format "payload_name:frame_number"

        input::
            payload_name (int,str): camera id
            frame_number (int): frame_number

        return::
            frame_id (str):
                frame_id in the form "payload_name:frame_number"
        """
        frame_id = "{0}:{1}".format( str(payload_name),
                                marvin.make_numbered_prefix(frame_number,6))
        return frame_id


    def close(self):
        self.cap.release()
