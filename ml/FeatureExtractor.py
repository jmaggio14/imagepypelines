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
                                        pooling=self.pooling_type


    Instantiation Args:
        network_name (str) = 'densenet121':
                    name of network to extract features from
        pooling_type (str) = 'avg':
                the type of pooling to perform on the features, must be
                one of ['max','avg']


    Example Use Case:
        network = FeatureExtractor('resnet50',pooling_type='avg')

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
    def __init__(self,
                 network_name='densenet121',
                 pooling_type='avg'
                 ):

        # Error Checking for the network occurs in self.__keras_importer
        self.model_fn, self.preprocess_fn, self.kerasimage\
            = self.__keras_importer(network_name,pooling_type)
        self.network_name = network_name
        self.pooling_type = pooling_type
        self.interpolation = interpolation

    @imsciutils.standard_image_input
    def extract_features(self, imgs):
        """
        Extracts image features from a the neural network specified in
        __init__

        input::
            imgs (np.ndarray,str,list): 2D or 3D image array or path to
                            image filename, or list of either
        returns::
            features (np.ndarray): features for this image
        """
        # Error checking for img occurs in __build_image_data
        imgs = self.__build_image_data(imgs)
        features = self.model_fn(imgs)
        # splitting features into a list
        features = [feature[i,:].flatten() for i in range(features.shape[0])]
        return features

    def __build_image_data(self, imgs):
        """
        this function turns an input numpy array or image path into an
        array format which keras requires for network feeding
        that format being a 4D tensor (batch,rows,cols,bands)

        input::
            imgs (np.ndarray,str,list):
                    image or path to image to be processed, or list of either
        returns::
            img_data (np.ndarray):
                    4D numpy array of the form (1,rows,cols,bands)
        """
        img_data = []
        for img in imgs:
            # checking to see if img is a path to an image
            if isinstance(img, str):
                assert os.path.exists(img), "{} is not a valid filename".format(img)
                img = self.kerasimage.load_img(img)
                img = self.kerasimage.img_to_array(img)
            # otherwise the image must be numpy array so it can be processed
            elif not isinstance(img, np.ndarray):
                raise ValueError("img must be a numpy array or path to image file")

            # must be (batches,rows,cols,bands) --> batch should be 1 for this case
            if img.ndim <= 3:
                r, c, b, _ = imsciutils.dimensions(img)
                img = img.reshape((1, r, c, b))

            img_data.append(img)
        # stacking all the images into a 4D array
        img_data = np.vstack(img_data)
        # preprocessing the image
        img_data = self.preprocess_fn(img_data)
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
            3) kerasimage (module):
                pointer to keras.image
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
        from keras import image as kerasimage
        return model_fn, preprocess_fn, kerasimage


# END
