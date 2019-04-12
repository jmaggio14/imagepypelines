# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018-2019 Jeff Maggio, Nathan Dileas, Ryan Hartzell
import os
from ..imports import import_opencv
from ..constants import IMAGE_EXTENSIONS

cv2 = import_opencv()

def prevent_overwrite(filename,create_file=False):
    """
    checks to see if a file or directory already exists and creates a
    new filename if it does. It can also create the file if specificed

    when creating a file, this function assumes that if there is no file
    extension then it should create a directory

    NOTE:
        This function creates unique filenames by creating them and
        checking their current existence. THIS CAN BE A SLOW
        PROCESS -- it is much more efficient to keep track of filenames
        internally in your application

    Args:
        filename (str): the full file or directory path to be
            overwrite protected
        create_file (bool): Default is False
            boolean indicating whether or not to create the file
            before returning

    Returns:
        str: the assuredly unique output filename
    """
    base_filename,extension = os.path.splitext(filename)
    out_filename = filename
    file_exists = os.path.exists(out_filename)
    num = 1


    while file_exists:
        out_filename = "{base}({num}){ext}".format(base=base_filename,
                                        num=make_numbered_prefix(num,0),
                                        ext=extension)
        num += 1
        file_exists = os.path.exists(out_filename)

    if create_file:
        if extension == "":
            input_is_directory = True
        else:
            input_is_directory = False

        if input_is_directory:
            os.makedirs(out_filename)
        else:
            base_path = os.path.split(out_filename)[0]
            if not os.path.exists(base_path):
                os.makedirs(base_path)
            with open(out_filename,'w') as out:
                out.write('')

    return out_filename


def make_numbered_prefix(file_number,number_digits=5):
    """
    returns a number string designed to be used in the prefix of
    systematic outputs.

    example use case
        "00001example_output_file.txt"
        "00002example_output_file.txt"

    Args:
        file_number (int): the number you want to prefix
        number_digits (int): minimum number of digits in the output
            string. Default is 5
    Returns:
        str: string of numbers with standard at least
            'number_digits' of digits
    """
    file_number = int( file_number )
    if file_number < 0:
        file_number_is_negative = True
    else:
        file_number_is_negative = False

    file_number_string = str( abs(file_number) )
    len_num_string = len(file_number_string)

    if len_num_string < number_digits:
        prefix = '0' * int(number_digits - len_num_string)
    else:
        prefix = ''

    if file_number_is_negative:
        prefix = '-' + prefix

    numbered_string = prefix + file_number_string
    return numbered_string


def convert_to(fname, format, output_dir=None, no_overwrite=False):
    """converts an image file to the specificed format
    "example.png" --> "example.jpg"

    Args:
        fname (str): the filename of the image you want to convert
        format (str): the format you want to convert to, acceptable options are:
            'png','jpg','tiff','tif','bmp','dib','jp2','jpe','jpeg','webp',
            'pbm','pgm','ppm','sr','ras'.
        output_dir (str,None): optional, a directory to save the reformatted
            image to. Default = None
        no_overwrite (bool): whether of not to prevent this function from
            overwriting a file if it already exists. see
            :prevent_overwrite:~`imagepypelines.io.prevent_overwrite` for
            more information

    Returns:
        str: the output filename that the converted file was saved to
    """
    # eg convert .PNG --> png if required
    format = format.lower().replace('.','')

    file_path, ext = os.path.splitext(fname)
    if output_dir is None:
        out_name = file_path + '.' + format
    else:
        basename = os.path.basename(file_path)
        out_name = os.path.join(output_dir, basename + '.' + format)


    if format not in IMAGE_EXTENSIONS:
        raise TypeError("format must be one of {}".format(IMAGE_EXTENSIONS))


    if no_overwrite:
        # check if the file exists
        out_name = prevent_overwrite(out_name)

    img = cv2.imread(fname)
    if img is None:
        raise RuntimeError("Unable to open up file {}".format(fname))

    cv2.imwrite(out_name, img)

    return out_name




# END
