# imagepypelines tutorials

## building your own pipeline
Pipelines are constructed of `blocks` which are simply objects that take in data,
process it, and output the processed data. Pipelines simply provide a high level
interface to control and apply processing algorithms for your workflows.

![pipeline](./docs/images/pipeline-example.png "pipeline example")

#### let's create an example fourier transform pipeline
```python
import imagepypelines as ip

loader = ip.ImageLoader() # load in image filenames
grayscale = ip.Color2Gray() # convert images to grayscale
fft = ip.FFT() # create an fft

fft_pipeline = ip.Pipeline([loader,grayscale,fft])

# load in a list of example image filenames
filenames = ip.standard_image_filenames()
# process the data
ffts = fft_pipeline.process(filenames)
```

### Simple Input Output Operations
Most blocks built into `imagepypelines` are made to work with imagery, but pipelines
are equally capable of performing IO output operations

#### loading images, process them, and saving them to disk
Thresholding pipeline, read images off of the disk, perform otsu thresholding,
and then save them to disk
```python
import imagepypelines as ip

standard_image_filenames = ip.standard_image_filenames()

# build blocks for this pipeline
loader = ip.ImageLoader()
otsu = ip.Otsu()
writer = ip.WriterBlock('./output_dir',return_type='filename')

# pipeline construction
pipeline = ip.Pipeline([loader,otsu,writer])

# get filenames of saved thresholded data
processed_filenames = pipeline.process(standard_image_filenames)
```


#### Pulling imagery off of a webcam and injecting it directly into a pipeline
_this is also a good example of how blocks can inject data into a pipeline. A block with a single input can result in N outputs_
```python
import imagepypelines as ip

# let's make a pipeline to talk to a webcam and save them to disk
camera = ip.CameraBlock(device='/dev/video0')
otsu = ip.Otsu()
writer = ip.WriterBlock(output_dir='./output_dir')

# pipeline construction
pipeline = ip.Pipeline(blocks=[camera,otsu,writer])

# run loop until there's a keyboard interrupt
while True:
    pipeline.process([10]) # capture 10 images and save them to disk
```
### Machine Learning Applications
One of the more powerful applications of `imagepypelines` is it's ease of use in
_machine learning_ and _feature engineering_ applications. We can easily build
a simple image classifier that is tailored to your purposes

#### Classification using a neural network
You can tweak this example with your own _image data_ and _hyperparameters_ to make a classifier for your own applications.
_this classifier is available as a builtin Pipeline with fully tweakable hyperparameters as **ip.SimpleImageClassifier**_
```python
import imagepypelines as ip

# ----------------- loading example data ---------------
cifar10 = ip.Cifar10()
train_data, train_labels = cifar10.get_train()
test_data, ground_truth = cifar10.get_test()

# --------------- now we'll build the pipeline ----------------
features = ip.PretrainedNetwork() # image feature block
pca = ip.PCA(256) # principle component analysis block
neural_network = ip.MultilayerPerceptron(neurons=512, num_hidden=2) # neural network block

classifier = ip.Pipeline([features,pca,neural_network])

# -------------- train and predict the classifier ---------------
classifier.train(train_data,train_labels) # train the classifier
predictions = classifier.process(test_data) # test the classifier

# print the accuracy
accuracy = ip.accuracy(predictions,ground_truth)
print('accuracy: {}%'.format(accuracy * 100) )
```

#### Classification using a Support Vector Machine
```python
import imagepypelines as ip

# ----------------- loading example data ---------------
cifar10 = ip.Cifar10()
train_data, train_labels = cifar10.get_train()
test_data, ground_truth = cifar10.get_test()

# --------------- now we'll build the pipeline ----------------
features = ip.PretrainedNetwork() # image feature block
pca = ip.PCA(256) # principle component analysis block
neural_network = ip.LinearSvm() # support vector machine block
# SVMs for linear, rbf, polynomial, and sigmoid kernels are all available

classifier = ip.Pipeline([features,pca,neural_network])

# -------------- train and predict the classifier ---------------
classifier.train(train_data,train_labels) # train the classifier
predictions = classifier.process(test_data) # test the classifier

# print the accuracy
accuracy = ip.accuracy(predictions,ground_truth)
print('accuracy: {}%'.format(accuracy * 100) )
```

#### 10 fold cross-validation using your own dataset
```python
import imagepypelines as ip
# for this example, we'll use the builtin SimpleImageClassifier pipeline,
# to get good results you may have to further customize this example
# or create your own pipeline
pipeline = ip.SimpleImageClassifier()

# --------------- load the filenames of our dataset ---------------
dataset_manager = ip.ml.DatasetManager(k_folds=10)
dataset_manager.load_from_directories(
                                'replace_with_your_own_image_class_directory1/',
                                'replace_with_your_own_image_class_directory2/',
                                'replace_with_your_own_image_class_directory3/')

all_accuracies = []
# testing this classifier 10 times using 10 fold cross-validation
for train_x,train_y,test_x,ground_truth in dataset_manager:
  pipeline.train(train_x,train_y)
  predicted = pipeline.process(test_x)
  all_accuracies.append( ip.accuracy(predicted,ground_truth) * 100 )

# calculating a 95% confidence interval
accuracy, h = ip.confidence_95( all_accuracies )
print("accuracy with 95 CI: {}% +/- {}%".format(accuracy,h))
```

## Creating your own block
There are two types of blocks in `imagepypelines`: **Simple Blocks** - blocks that process one piece of data at a time, and **Batch Blocks** - blocks that process multiple pieces of data at a time.

In practical terms, this merely manifests itself as a function that takes a list of data _(batch blocks)_ or a function that takes in a single datum _(simple blocks)_

### Batch Blocks
Batch processing _(the act of processing multiple pieces of data at the same time)_ is typically used when you are utilizing GPUs or other types of hardware acceleration in your processing pipeline.

They can make your pipelines **much** more efficient, this is typically because sending data between the _CPU_ & _GPU_ is slow process. Sending 100 images separately is slower than sending 100 images at once. Practically, all this really means is that having a system capable of processing multiple pieces of data can optimize your pipeline.

Batch Processing blocks in `imagepypelines` simply contain a processing function that takes in a list of data and returns a list of data.

Lets create a super simple example just to demonstrate how you can create a batch processing block in `imagepypelines`.
```python
import imagepypelines as ip

class AddOneBlock(ip.BatchBlock):
    def __init__(self):
        io_map = {ip.RgbImage():ip.RgbImage()}
        super(AddOneBlock,self).__init__(io_map)

    def batch_process(self,batch_data):
        """take in a list of datums and return a processed list of datums"""
        # turn this list of data into a single array
        img_stack = np.stack(batch_data, axis=0) # [(N,M,3),(N,M,3)] --> (2,N,M,3)
        img_stack = img_stack + 1 # add one to images
        # (2,N,M,3) --> [(N,M,3),(N,M,3)]
        processed_batch = [img_stack[i] for i in range(img_stack.shape[0])]
        return processed_batch
```

The above block does batch processing on multiple images, but could have been done easier and just as efficiently without batch processing.

Let's create a more complex example that utilizes the GPU using tensorflow
```python
import imagepypelines as ip
import tensorflow as tf
import numpy as np

class AddOneBlock(ip.BatchBlock):
    def __init__(self):
        self._setup_tf_graph()
        io_map = {ip.RgbImage():ip.RgbImage()}
        super(AddOneBlock,self).__init__(io_map)

    def _setup_tf_graph(self):
      """we'll build our tensorflow graph in here"""
      graph = tf.Graph()
      with graph.as_default():
        batch_data = tf.placeholder(tf.float32,name='batch_data') # this value will be fed in
        one = tf.constant(1.0) # create a tensor = 1
        tf.math.add(batch_data,one,name="processed")

      self.sess = tf.Session(graph=graph)


    def batch_process(self,batch_data):
        """take in a list of datums and return a processed list of datums"""
        # feed data in and extract the final tensor we named 'processed'
        processed = self.sess.run('processed:0',{'batch_data:0':batch_data})
        processed = [processed[i] for i in range(processed.shape[0])]
        return processed


```



### Simple Blocks
Simple Blocks on the other hand simply process one piece of data at a time
