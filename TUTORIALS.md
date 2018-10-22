# imsciutils tutorials

## building your own pipeline
Pipelines are constructed of `blocks` which are simply objects that take in data,
process it, and output the processed data. Pipelines simply provide a high level
interface to control and apply processing algorithms for your workflows.

![pipeline](https://github.com/jmaggio14/imsciutils/blob/develop/docs/images/pipeline-example.png "pipeline example")

#### let's create an example fourier transform pipeline
```python
import imsciutils as iu

loader = iu.ImageLoader() # load in image filenames
grayscale = iu.Color2Gray() # convert images to grayscale
fft = iu.FFT() #create an fft

fft_pipeline = iu.Pipeline([loader,grayscale,fft])

# load in a list of example image filenames
filenames = iu.standard_image_filenames()
# process the data
ffts = fft_pipeline.process(filenames)
```

### Machine Learning Applications
One of the more powerful applications of `imsciutils` is it's ease of use in
_machine learning_ and _feature engineering_ applications. We can easily build
a simple image classifier that is tailored to your purposes

#### all in one image classifier
You can tweak this example with your own _image data_ and _hyperparameters_ to make a classifier for
your own applications
```python
import imsciutils as iu

# ----------------- loading example data ---------------
cifar10 = iu.Cifar10()
train_data, train_labels = cifar10.get_train()
test_data, ground_truth = cifar10.get_test()

# --------------- now we'll build the pipeline ----------------
features = iu.PretrainedNetwork() # image feature block
pca = iu.PCA(256) # principle component analysis block
neural_network = iu.MultilayerPerceptron(neurons=512, num_hidden=2) # neural network block

classifier = iu.Pipeline([features,pca,neural_network])

# -------------- train and predict the classifier ---------------
classifier.train(train_data,train_labels) # train the classifier
predictions = classifier.process(test_data) # test the classifier

# print the accuracy
accuracy = iu.accuracy(predictions,ground_truth)
print('accuracy: {}%'.format(accuracy * 100) )
```
_this classifier is available with fully tweakable hyperparameters as **iu.SimpleImageClassifier**_


#### 10 fold cross-validation using your own dataset
```python
import imsciutils as iu
# for this example, we'll use the builtin SimpleImageClassifier pipeline,
# to get good results you may have to further customize this example
# or create your own pipeline
pipeline = iu.SimpleImageClassifier()

# --------------- load the filenames of our dataset ---------------
dataset_manager = iu.ml.DatasetManager(k_folds=10)
dataset_manager.load_from_directories(
                                'replace_with_your_own_image_class_directory1/',
                                'replace_with_your_own_image_class_directory2/',
                                'replace_with_your_own_image_class_directory3/')

all_accuracies = []
# testing this classifier 10 times using 10 fold cross-validation
for train_x,train_y,test_x,ground_truth in dataset_manager:
  pipeline.train(train_x,train_y)
  predicted = pipeline.process(test_x)
  all_accuracies.append( iu.accuracy(predicted,ground_truth) * 100 )

# calculating a 95% confidence interval
accuracy, h = iu.confidence_95( all_accuracies )
print("accuracy with 95 CI: {}% +/- {}%".format(accuracy,h))
```


####
