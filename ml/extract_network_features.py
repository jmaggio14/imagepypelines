from importlib import import_module
import cv2
import numpy as np
from keras imort image

class extract_features(object):
    __SUBMODULES = {'xception':'keras.applications.xception',
                    'vgg16':'keras.applications.vgg16',
                    'vgg19':'keras.applications.vgg19',
                    'resnet50','keras.applications.resnet50',
                    'inception_v3':'keras.applications.inception_v3',
                    'inception_resnet_v2':'keras.applications.inception_resnet_v2',
                    'mobilenet':'keras.applications.mobilenet',
                    'densenet121':'keras.applications.densenet',
                    'densenet169':'keras.applications.densenet',
                    'densenet201':'keras.applications.densenet',
                    'nasnetlarge':'keras.applications.nasnet',
                    'nasnetmobile':'keras.applications.nasnet',
                    'mobilenetv2':'keras.applications.mobilenetv2',
                    }
    __FUNCTION_NAMES = {'xception':'Xception',
                        'vgg16':'VGG16',
                        'vgg19':'VGG19',
                        'resnet50':'ResNet50',
                        'inception_v3':'InceptionV3',
                        'inception_resnet_v2':'InceptionResNetV2',
                        'mobilenet':'MobileNet',
                        'densenet121':'DenseNet121',
                        'densenet169':'DenseNet169',
                        'densenet201':'DenseNet201',
                        'nasnetlarge':'NASNetLarge',
                        'nasnetmobile':'NASNetMobile',
                        'mobilenetv2':'MobileNetV2',
                        }
    __CACHED_MODEL_FNS = {}
    __CACHED_PREPROCESS_FNS = {}
    TARGET_SIZE = (299,299)
    def __call__(self,img,network_name='inception_v3',interpolation=cv2.INTER_AREA):
        model_fn,preprocess_fn = self.__keras_importer(network_name)
        img = self.__build_image_data(img,preprocess_fn)

        features = model_fn(img)
        return features

    def __build_image_data(self,img,preprocess_fn):
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
        """
        #checking to see if img is a path to an image
        if isinstance(img,str):
            img = image.load_img(img, target_size=self.TARGET_SIZE)
            img = image.img_to_array(img)
        #otherwise the image must be numpy array so it can be processed
        elif not isinstance(img,np.ndarray):
            raise ValueError("img must be a numpy array or path to image file")

        #checking to see if the image is the correct shape for the network
        if img.shape[:2] != self.TARGET_SIZE:
            img = cv2.resize(img,dsize=self.TARGET_SIZE)
        #must be (batches,rows,cols,bands) --> batch should be 1 for this case
        if img.ndim <= 3:
            r,c,b,_ = imgscitools.dimensions(img)
            img = img.reshape( (1,r,c,b) )

        #preprocessing the image
        img = preprocess_fn( img )
        return img

    def __keras_importer(self,network_name):
        """
        retrieves the feature extraction algorithm and preprocess_fns
        from keras, only importing the desired model specified by the
        network name

        It will also cache the built models so they can be accessed
        quickly later without reinstantiation
        """
        #if the model_fn already exists, retrieve it to save time instantiating
        if network_name in self.__CACHED_MODEL_FNS:
            model_fn = self.__CACHED_MODEL_FNS[network_name]
            preprocess_fn = self.__CACHED_PREPROCESS_FNS[network_name]
            return model_fn,preprocess_fn


        #checking to make sure network_name is valid
        if network_name not in self.__SUBMODULES:
            error_string = "unknown network '{network_name}', \
                            network_name must be one of {network_list}"
                            .format(network_name=network_name,
                                    network_list=self.__SUBMODULES.keys())
            raise ValueError(error_string)

        #importing the proper keras model_fn and preprocess_fn
        submodule = import_module(self.__SUBMODULES[network_name])
        model_fn = getattr(submodule,self.__FUNCTION_NAMES[network_name])
        model_fn = model_fn(include_top=False,weights='imagenet',pooling='max')
        preprocess_fn = getattr(submodule,'preprocess_input')

        #adding new models to the existing dictionary
        self.__CACHED_MODEL_FNS[network_name] = model_fn
        self.__CACHED_PREPROCESS_FNS[network_name] = preprocess_fn

        return model_fn,preprocess_fn
















# END
