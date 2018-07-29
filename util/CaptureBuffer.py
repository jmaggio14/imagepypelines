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
import collections

from marvin.payload import Payload

class CaptureBuffer(Payload):
    """
    An object meant to buffer an array of marvin.Frame objects for later
    retrieval. These buffers are designed to be used in a
    last in - first out design, but have the ability to retreive a frame
    using it's id or index into the buffer

    Instantiation Args::
        buffer_size (int) = 30:
                the number of frames to be stored in the buffer

    attributes::
        buffer_size (int): input buffer size cast to an int
        buffer (dict): a dictionary which stores the frame containers
                            with the frame id as the key
        order (deque): a list of frame ids which indicates the order of
                        the frames in the buffer.
                        (oldest id is at the end of the list)

    functions::
        --------------- Overwritten Payload Functions ------------
        capture(frame):
                    adds an input frame to the buffer
        retrieve(key_index=0):
                    retrieves a frame or set of frames from the buffer
        change_setting(setting,value):
                    changes a buffer setting
        get_status(query):
                    returns a queried buffer attribute
        close():
                    deletes everything currently stored in the buffer


        -------------- Additional functions -----------------

        get_newest():
                returns the newest frame off the buffer
        get_oldest():
                returns the oldest frame off the buffer
        get_all():
                returns all frames off the buffer
        get_by_list(index_key_list):
                returns a list of frames defined by an input list
        get_by_index(index):
                returns a frame according an index into the buffer
        get_by_id(frame_id):
                returns a frame according a frame_id index

    properties::
        None

    """
    def __init__(self,buffer_size=30):
        self.buffer_size = int(buffer_size)
        self.buffer = {}
        self.order = collections.deque()


    def retrieve(self,key_index=0):
        """
        retrieves frames off the buffers using either a frame_id, or a
        an index into the buffer, or list of either.
        e.g.
            capture_buffer[frame_id]
                `--> returns capture_buffer.get_by_id(frame_id)
            capture_buffer[0]
                `--> returns capture_buffer.get_by_index(0)
            capture_buffer[ [0,5,frame_id1] ]
                `--> returns capture_buffer.get_by_list( [0,5,frame_id1] )


        input::
            key_index (str,int,list):
                    key, index or list of both to index into the buffer
        return::
            frame (list,marvin.Frame):
                            the frame(s) at the key_index location(s)
        """
        if key_index == "all":
            return self.get_all()

        if isinstance(key_index,str):
            return self.get_by_id( key_index )

        elif isinstance(key_index,int):
                return self.get_by_index( key_index )

        elif isinstance(key_index,(list,tuple)):
                return self.get_by_list( key_index )
        else:
            raise Marvin.quadcam.CaptureBufferIndexError(key_index=key_index)


    def change_setting(self,setting,value):
        """
        changes the setting specified to the desired value

        Args:
            settings (str): the setting to change, currently the only
                changeable setting is "buffer_size"
            value (any type): the value the setting should be changed to
        """
        if setting == "buffer_size":
            # checking if value is int or float
            if isinstance(buffer_size,(int,float)):
                self.buffer_size = int( value )
            else:
                raise ValueError("buffer_size must be a number")
        else:
            raise ValueError("setting param must be one of ('buffer_size')")



    def get_status(self,query):
        """query the capture buffer for data about its status

        Args:
            query (string): indicator for which data to return
                possible options are:
                "buffer_size" --> size of the buffer
                "frame_ids"  --> all frame_ids ordered newest-oldest

        Returns:
        data (list,int): the requested data specified by the query

        """
        if query == "buffer_size":
            return self.buffer_size
        elif query == "frame_ids":
            return list( self.order )
        else:
            raise ValueError("query can only be 'buffer_size' or 'frame_ids'")

    def capture(self,frame):
        """adds a frame to the buffer and updates the internal queue.
        if the buffer becomes larger than the specified buffer size,
         then the oldest value is deleted

        input::
            frame: marvin.Frame object of the input image
        return::
            None
        """
        if isinstance(frame,marvin.Frame):
            self.buffer[ frame.id ] = frame
            #insert the value at the beginning of the order
            self.order.appendleft( frame.id )

            if len(self.buffer) > self.buffer_size:
                #deleting the last value in the buffer and the corresponding value in self.order
                del self.buffer[ self.order[-1] ]
                del self.order[-1]


    def close(self):
        """clears the buffer of images

        Args:
            None
        Returns:
            Nones
        """
        self.order.clear()
        self.buffer.clear()




    #------------------------ user_funcs ------------------------

    def get_newest(self):
        """
        grabs the newest frame off the buffer, ie the most recent one
        added to the buffer

        input::
            None
        return::
            newest (marvin.Frame): the most recent frame off the buffer
        """
        newest = self.get_by_index(0)
        return newest


    def get_oldest(self):
        """
        grabs the oldest frame off the buffer, ie the least recent one
        in the buffer

        input::
            None
        return::
            oldest (marvin.Frame): the oldest frame off the buffer
        """
        oldest = self.get_by_index(-1)
        return oldest


    def get_all(self):
        """
        returns all the frames in the buffer in order of newest-->oldest

        input::
            None
        frames::
            frames (list):: list of all marvin.Frame objects ordered
                newest = ret[0]
                oldest = ret[-1]
        """
        frames = self.get_by_list( self.order )
        return frames


    def get_by_list(self,index_key_list):
        """
        this function will treat each value in this list as an index or
        frame_id into the buffer returns a list of frames of equal
        length to 'input1', None if id or index doesn't not exist

        input::
            index_key_list (list,tuple): list of indices to parse and
                    retrieve frames for
        return::
            frames (list): list of frames, retrieved by index or id
        """
        frames = []
        for i in index_key_list:
            if isinstance(i,int):
                frames.append( self.__get_by_index(i) )

            elif isinstance(i,str):
                frames.append( self.__get_by_id(i) )

            else:
                raise marvin.quadcam.CaptureBufferIndexError(key_index=i)
                frames.append(None)
                # frames.append( marvin.DebugImage( debug_message ) )

        return frames


    def get_by_index(self,index):
        """
        retrieves the frame defined by an index value into the buffer
        e.g.
            getByIndex(9) --> returns the 10th frame off the buffer

        input::
            index (int): the index into the buffer
        return::
            frame (marvin.Frame,marvin.DebugImage): the frame
                    at self.buffer[ self.order[index] ]
        """
        try:
            frame_id = self.order[index]
            return self.get_by_id( frame_id )
        except IndexError:
            debug_message = "INVALID INDEX: {0} for indexing into capture\
                                    buffer".format(index)
            marvin.Status.warning( debug_message )
            # return marvin.DebugImage(message=debug_message)
            return None


    def get_by_id(self,frame_id):
        """
        retrieves the associated with that frame_id in the buffer
        e.g.
            get_by_id("0:0027") --> the frame with the id "0:0027"

        input::
            frame_id (str): the frame id of the frame to be indexed
        return::
            frame (marvin.Frame): the frame at self.buffer[frame_id]
        """
        try:
            frame = self.buffer[ frame_id ]
            marvin.Status.debug("returning frame: {0} from the buffer \
                            at index: {1}".format(frame.id,
                                            self.getIndexOfFrameId(frame.id)))
            return frame
        except KeyError:
            debug_message = "INVALID FRAME ID: {0} for indexing into buffer. \
                                valid ids are {1}".format(frame_id,
                                                        self.buffer.keys())
            marvin.Status.warning( debug_message )
            # return marvin.DebugImage( debug_message )
            return None


    def get_index_of_frame_id(self,frame_id):
        """
        Retrieves the index of a frame_id off of the buffer, if the
        frame corresponding to that frame_id doesn't exist in the
        buffer, then None is returned

        input::
            frame_id (marvin.FrameId): the input frame_id
        return::
            index (None,int): The index of the frame_id in the buffer,
            or None if it doesn't exist

        NOTE::
            It may be more prudent to raise a custom marvinException
            instead of returning None
        """
        if frame_id in self.order:
            index = self.order.index( frame_id )
        else:
            marvin.Status.warning( "frame_id: {0} does not exist in \
                                        this buffer".format( frame_id ) )
            index = None

        return index
