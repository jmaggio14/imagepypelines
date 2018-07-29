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

class RtspServer(object):
    """
    IN ACTIVE DEVELOPMENT AS OF APRIL 16, 2018
    """
    def __init__(self,
                    host="127.0.0.1",
                    port=5000,
                    threads=2,
                    fps=0,
                    encoder=None):
        if encoder == None:
            encoder = marvin.GSTREAMER_ENCODER_X264
        self.fps = fps
        self.__gstreamer_kwargs = {"host":host,
                                    "port":port,
                                    "threads":threads}
        self.gstreamer_string = "appsrc ! videoconvert ! x264enc ! \
                                video/x-h264 threads={threads}! rtph264pay !\
                                 udpsink host={host} port={port}"
                                 .format(**self.__gstreamer_kwargs)
#
#
    def __initializeWriter(self,width,height):
        # self.streamer = cv2.VideoWriter( filename=self.gstreamer_string,fourcc=0,frameSize=(width,height) )
        self.streamer = cv2.VideoWriter( filename=self.gstreamer_string,
                                            fourcc=0,
                                            fps =self.fps,
                                            frameSize=(width,height) )
        marvin.Status.info("initialized RtspStreamer operating on {threads}\
                            threads via host: {host}:{port}"
                            .format(**self.__gstreamer_kwargs))
#
    def write(self,frame):
        if not hasattr(self,"streamer"):
            self.__initializeWriter( frame.shape[1],frame.shape[0] )
#
        self.streamer.write(frame)
#
    def release(self):
        self.streamer.release()
#
    def open(self):
        self.streamer.open()
#
