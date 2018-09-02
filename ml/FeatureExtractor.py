from importlib import import_module
import cv2
import numpy as np
import imsciutils


class FeatureExtractor(object):
    """
    Class to extract features from pretrained neural networks
    trained on imagenet with max pooling applied.

    This class utilizes keras to automatically leverage
    hardware resources and retrieve pretrained networks.
    available networks are:
                            - xception
                            - vgg16
                            - vgg19
                            - resnet50
                            - inception_v3
                            - inception_resnet_v2
                            - mobilenet
                            - densenet121
                            - densenet169
                            - densenet201
                            - nasnetlarge
                            - nasnetmobile
                            - mobilenetv2

    see: https://keras.io/applications/ for more details
    kwargs for network instantiation are:
                                        include_top=False,
                                        weights='imagenet',
                                        pooling='max'


    Instantiation Args:
        network_name (str): name of network to extract features from
        interpolation (cv2 constant): type of interpolation used to
                                        resize images

    Example Use Case:
        network = FeatureExtractor('resnet50')

        img = imsciutils.lenna()
        lenna_features = network.extract_features(img)

    """
    __SUBMODULES = {'xception': 'keras.applications.xception',
                    'vgg16': 'keras.applications.vgg16',
                    'vgg19': 'keras.applications.vgg19',
                    'resnet50': 'keras.applications.resnet50',
                    'inception_v3': 'keras.applications.inception_v3',
                    'inception_resnet_v2': 'keras.applications.inception_resnet_v2',
                    'mobilenet': 'keras.applications.mobilenet',
                    'densenet121': 'keras.applications.densenet',
                    'densenet169': 'keras.applications.densenet',
                    'densenet201': 'keras.applications.densenet',
                    'nasnetlarge': 'keras.applications.nasnet',
                    'nasnetmobile': 'keras.applications.nasnet',
                    'mobilenetv2': 'keras.applications.mobilenetv2',
                    }
    __FUNCTION_NAMES = {'xception': 'Xception',
                        'vgg16': 'VGG16',
                        'vgg19': 'VGG19',
                        'resnet50': 'ResNet50',
                        'inception_v3': 'InceptionV3',
                        'inception_resnet_v2': 'InceptionResNetV2',
                        'mobilenet': 'MobileNet',
                        'densenet121': 'DenseNet121',
                        'densenet169': 'DenseNet169',
                        'densenet201': 'DenseNet201',
                        'nasnetlarge': 'NASNetLarge',
                        'nasnetmobile': 'NASNetMobile',
                        'mobilenetv2': 'MobileNetV2',
                        }
    TARGET_SIZE = (299, 299)

    def __init__(self,
                 network_name='inception_v3',
                 pooling_type='avg',
                 interpolation=cv2.INTER_AREA):

        # Error Checking for the network occurs in self.__keras_importer
        if interpolation not in imsciutils.CV2_INTERPOLATION_TYPES:
            error_string = "interpolation type must be one of {}"\
                .format(imsciutils.CV2_INTERPOLATION_TYPES)
            raise ValueError(error_string)

        self.model_fn, self.preprocess_fn, self.kerasimage\
            = self.__keras_importer(network_name,pooling_type)
        self.network_name = network_name
        self.pooling_type = pooling_type
        self.interpolation = interpolation

    @imsciutils.standard_image_input
    def extract_features(self, img):
        """
        Extracts image features from a the neural network specified in
        __init__

        input::
            img (np.ndarray): 2 or 3 image array
        returns::
            features (np.ndarray): features for this image
        """
        # Error checking for img occurs in __build_image_data
        img = self.__build_image_data(img)
        features = self.model_fn(img)
        return features

    def __build_image_data(self, img):
        """
        this function turns an input numpy array or image path into an
        array format which keras requires for network feeding
        that format being a 4D tensor (batch,rows,cols,bands)
        (batch size will be always be 1 in this case)

        input::
            img (np.ndarray,str):
                    image or path to image to be processed
            preprocess_fn (func):
                    preprocessing function for image data, output from
                    self.__keras_importer
        returns::
            img_data (np.ndarray):
                    4D numpy array of the form (1,rows,cols,bands)
        """
        # checking to see if img is a path to an image
        if isinstance(img, str):
            assert os.path.exists(img), "img must be valid filename or array"
            img = image.load_img(img, target_size=self.TARGET_SIZE)
            img = image.img_to_array(img)
        # otherwise the image must be numpy array so it can be processed
        elif not isinstance(img, np.ndarray):
            raise ValueError("img must be a numpy array or path to image file")

        # checking to see if the image is the correct shape for the network
        if img.shape[:2] != self.TARGET_SIZE:
            img = cv2.resize(img, dsize=self.TARGET_SIZE)

        # must be (batches,rows,cols,bands) --> batch should be 1 for this case
        if img.ndim <= 3:
            r, c, b, _ = imsciutils.dimensions(img)
            img = img.reshape((1, r, c, b))

        # preprocessing the image
        img_data = self.preprocess_fn(img)
        return img_data

    def __keras_importer(self, network_name, pooling_type):
        """
        Retrieves the feature extraction algorithm and preprocess_fns
        from keras, only importing the desired model specified by the
        network name.

        input::
            network_name (str):
                name of the network being used for feature extraction
            pooling_type (str):
                type of pooling you want to use ('avg' or 'max')

        returns::
            1) model_fn (func):
                function that extract features from the NN
            2) preprocess_fn (func):
                function that preprocesses the image for the network
        """
        # checking to make sure network_name is valid
        if network_name not in self.__SUBMODULES:
            error_string = "unknown network '{network_name}', \
                            network_name must be one of {network_list}"\
                                .format(network_name=network_name,
                                        network_list=self.__SUBMODULES.keys())
            raise ValueError(error_string)

        assert pooling_type in ['avg','max'],"'pooling_type' must be one of the following strings ['avg','max']"

        # importing the proper keras model_fn and preprocess_fn
        submodule = import_module(self.__SUBMODULES[network_name])
        model_constructor = getattr(submodule,
                                    self.__FUNCTION_NAMES[network_name])
        model_fn = model_constructor(include_top=False,
                                     weights='imagenet',
                                     pooling=pooling_type)

        preprocess_fn = getattr(submodule, 'preprocess_input')

        return model_fn, preprocess_fn


# END
