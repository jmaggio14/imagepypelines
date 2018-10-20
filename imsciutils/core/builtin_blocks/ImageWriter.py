from .. import SimpleBlock
from .. import ArrayType
from ... import util
import cv2
import os




class ImageWriter(SimpleBlock):
    """
    Block that operates as a system that saves single frames to a
    specified output directory.

    this block will not impact dataflow through the pipeline and will return
    whatever images are passed into it

    every new frame passed in will be saved in the following format:
        output_dir/000001base_filename.png
        output_dir/000002base_filename.png
        output_dir/000003base_filename.png
        ...

    Args:
        output_dir (str):
            path to output directory that images will be saved to
        base_filename (str): default is 'image.png'
            filename common among all images, these will be incremented
            numerically with each new image saved
    """
    def __init__(self,output_dir,
                        base_filename='image.png',
                        ):

        assert isinstance(output_dir, str), "'output_dir' must be str"
        assert isinstance(base_filename, str), "'base_filename' must be str"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        self.output_dir = output_dir
        self.base_filename = base_filename
        self.image_number = 0


        io_map = {ArrayType([None,None,3]):ArrayType([None,None,3]),
                    ArrayType([None,None]):ArrayType([None,None])}

        super(ImageWriter,self).__init__(io_map,
                                            requires_training=False,
                                            requires_labels=False)


    def process(self, datum):
        """
        writes an image frame to the specificed directory, forces
        resizing if specified when the class is instantiated

        Args:
            datum (np.ndarray): frame to be saved to the output_dir

        Returns:
            datum (np.ndarray): frame to be saved to the output_dir
        """
        self.image_number += 1
        image_number = util.make_numbered_prefix(self.image_number,6)
        out_filename = os.path.join(self.output_dir,
                                    image_number + self.base_filename)

        if not isinstance(self.size, type(None)):
            datum = cv2.resize(datum,
                               dsize=(self.size[1], self.size[0]),
                               interpolation=self.interpolation)

        cv2.imwrite(filename, datum)
        return datum
