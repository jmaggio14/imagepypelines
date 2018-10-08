from ... import io
from ... import util
from .. import BatchBlock




class CameraBlock(BatchBlock):
    def __init__(self,device=0,fourcc='MJPG',mode='count'):
        #JM: error checking for these values will occur in io.CameraCapture
        self.device = device
        self.fourcc = fourcc

        assert mode in ['count','time'], "'mode' must set to 'time' or 'count'"
        self.mode = mode

        input_shape = int,float
        output_shape = [None,None],[None,None,3]
        self.cap = io.CameraCapture(self.device,self.fourcc)
        super(CameraBlock,self).__init__(input_shape,
                                            output_shape,
                                            requires_training=False)

    def before_process(self,data,labels=None):
        images = []
        image_labels = []

        if labels is None:
            labels = [None]


        if self.mode == 'count':
            # data in this case should be a 1 element list with the number
            # of images to capture
            num_images = int(data[0])
            lbl = labels[0]
            for i in range(num_images):
                img = self.cap.retrieve()
                images.append(img)
                images_labels.append(lbl)

        elif self.mode == 'time':
            # data in this case should be a 1 element list with the number
            # of seconds to capture frames for
            num_seconds = float(data[0])
            lbl = labels[0]
            # JM: make timer to set a countdown until capture should stop
            t = util.Timer()
            t.countdown = num_seconds
            # JM: retrieve images until countdown hits zero
            while t.countdown:
                img = self.cap.retrieve()
                images.append(img)
                image_labels.append(lbl)

        # set captured images as a instance variable so it can be accessed
        # in batch_process
        self.images = images
        self.image_labels = image_labels


    def batch_process(self,data):
        # JM: return image list created in before_process
        return self.images

    def labels(self,labels):
        # JM: return label list created in before_process
        return self.image_labels


    def after_process(self):
        # JM: reset these values to empty lists to reduce idle memory footprint
        self.images = []
        self.image_labels = []
