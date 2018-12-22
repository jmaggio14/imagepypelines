<img src="https://raw.githubusercontent.com/jmaggio14/imagepypelines/91b5f297632df16c2c246492782e37ea0a263b45/docs/images/ip_logo.png" width="64">

# imagepypelines

![build](https://www.travis-ci.com/jmaggio14/imagepypelines.svg?branch=master "master build success")
[![codecov](https://codecov.io/gh/jmaggio14/imagepypelines/branch/master/graph/badge.svg)](https://codecov.io/gh/jmaggio14/imagepypelines)


The `imagepypelines` package consists of high level tools which simplify the construction of complex image processing, computer vision, and machine learning frameworks. During our time in the undergrad Imaging Science program at the Rochester Institute of Technology, we found ourselves writing and rewriting code for things as simple as data type casting and displaying imagery when debugging, causing more trouble than mathematical or logical bugs themselves! Our hope is that the plug-and-play, easily-customizable nature of `imagepypelines` will allow all data-driven scientists to construct complex frameworks quickly for prototyping applications, and serve as a valuable educational tool for those interested in learning traditionally tough subject matter in a friendly environment!

To achieve this goal, our development team always adheres to the following 5 core principles:

1. Legos are fun
2. Coding should be fun
3. Therefore coding should be like playing with Legos
4. Imagery is fun, so that will always be our focus
5. We must suffer, lest our users suffer

**_This project is currently in alpha_**

## Installation
_(make sure you see the **dependencies** section)_

Python compatibility: 3.4-3.6 (Python 2.7 backwards) 64bit

**via pip**:
```
pip install imagepypelines --user
```
**from source**:
```console
git clone https://github.com/jmaggio14/imagepypelines.git
cd imagepypelines
python setup.py install
```
### dependencies
for full functionality, imagepypelines requires _opencv_ and _tensorflow_ to be installed
on your machine
##### tensorflow
```console
pip install tensorflow-gpu --user
```
(or for cpu only)
```console
pip install tensorflow --user
```
##### opencv
we strongly recommend that you [build opencv from source](https://docs.opencv.org/3.4/df/d65/tutorial_table_of_content_introduction.html). **_However_** unofficial bindings for opencv can be installed with
```console
pip install opencv-python --user
```
(while we haven't encountered many problems with these unofficial bindings,
we do not guarantee support)


## Documentation
Full documentation for `imagepypelines`, including examples and tutorials, can be found on our website: www.imagepypelines.org


## Licensing / Credit
`imagepypelines` is licensed under the [MIT](https://choosealicense.com/licenses/mit/) permissive software license. You may use this code for research or commercial use so long as it conforms to the terms of the license included in this repo as well as the licenses of `imagepypelines` dependencies.

Please credit us if you use `imagepypelines` in your research
```
@misc{imagepypelines,
  title="imagepypelines - imaging science acceleration library",
  author="Hartzell, Dileas, Maggio",
  YEAR="2018",
  howpublished="\url{https://github.com/jmaggio14/imagepypelines}",
}
```

# What Makes Us Unique?

## The Pipeline
`imagepypelines`'s most powerful feature is a high level interface to create data processing pipelines which apply a sequence of algorithms to input data automatically.

In our experience as imaging scientists, processing pipelines in both corporate or academic settings are not always easy to adapt for new purposes and are therefore too often relegated to _proof-of-concept_ applications only. Many custom pipelines may also not provide step-by-step error checking, which can make debugging a challenge.
![xkcd](https://imgs.xkcd.com/comics/data_pipeline.png "cracked pipelines")

(source: [XKCD](https://www.xkcd.com/2054/))


The `Pipeline` object of `imagepypelines` allows for quick construction and prototyping, ensures end-to-end compatibility through each layer of a workflow, and leverages helpful in-house debugging utilities for use in image-centric or high-dimensional data routines.


## The Block
Pipelines in `imagepypelines` are constructed of processing `blocks` which apply an algorithm to a sequence of data passed into it.

![pipeline](https://raw.githubusercontent.com/jmaggio14/imagepypelines/91b5f297632df16c2c246492782e37ea0a263b45/docs/images/pipeline-example.png "pipeline example")

Each `block` _takes in_ a list of data and _returns_ a list of data, passing it onto the next block or out of the pipeline. This system ensures that blocks are compatible with algorithms that process data in batches or individually. Blocks also support label handling, and thus are **compatible with supervised machine learning systems or other algorithms that require training**

Broadly speaking, each box can be thought of as a black box which simply applies an operation to input data
![block](https://raw.githubusercontent.com/jmaggio14/imagepypelines/91b5f297632df16c2c246492782e37ea0a263b45/docs/images/block.png "block example")

a _datum_ can be anything: an image array, a filename, a label -- pretty much an pythonic type.


Blocks can also output more or less datums than they take in and are thus capable of being used for culling or injecting data into the pipeline.

### Hang on? are all blocks compatible with one another?
not entirely, each block has predefined acceptable inputs and outputs. However the `Pipeline` object will validate the pipeline integrity before any data is processed


## Building a pipeline
building a pipeline is super easy

### Image Display Pipeline
```python
import imagepypelines as ip

pipeline = ip.Pipeline(name='image display')
pipeline.add( ip.ImageLoader() ) # each one of these elements are 'blocks'
pipeline.add( ip.Resizer() )
pipeline.add( ip.BlockViewer() )

# now let's display some example data!
pipeline.process( ip.standard_image_filenames() )
```
We just made a processing pipeline that can read in images, resize them and display them! but we can do much more complicated operations.

### Lowpass Filter Pipeline
```python
import imagepypelines as ip

load = ip.ImageLoader()
resize = ip.Resizer(512,512)
fft = ip.FFT()
lowpass = ip.Lowpass(cut_off=32)
ifft = ip.IFFT()
display = ip.BlockViewer(pause_time=1)

pipeline = ip.Pipeline(blocks=[load,resize,fft,lowpass,ifft,display])


# process a set of images (using imagepypelines' example data)
filenames = ip.standard_image_filenames()
pipeline.process(filenames)
```

### Machine Learning Applications
One of the more powerful applications of `imagepypelines` is it's ease of use in
_machine learning_ and _feature engineering_ applications.
we can easily tailor a pipeline to perform image classification

this classifier is available as a builtin Pipeline with fully tweakable hyperparameters as **ip.SimpleImageClassifier**
```python
import imagepypelines as ip

features = ip.PretrainedNetwork() # image feature block
pca = ip.PCA(256) # principle component analysis block
neural_network = ip.MultilayerPerceptron(neurons=512, num_hidden=2) # neural network block

classifier = ip.Pipeline([features,pca,neural_network])

# loading example data
cifar10 = ip.Cifar10()
train_data, train_labels = cifar10.get_train()
test_data, ground_truth = cifar10.get_test()

classifier.train(train_data,train_labels) # train the classifier
predictions = classifier.process(test_data) # test the classifier

# print the accuracy
accuracy = ip.accuracy(predictions,ground_truth) * 100
print('pipeline classification accuracy is {}%!'.format(accuracy))
```

We just trained a full neural network classifier!


### Processing Blocks built into imagepypelines
_more are being added with every commit!_

#### I/O operations
- Image Display
- Camera Capture
- Image Loader
- Image Writing

#### Machine Learning
- Linear Support Vector Machine
- Rbf Support Vector Machine
- Poly Support Vector Machine
- Sigmoid Support Vector Machine
- trainable neural networks
- 8 Pretrained Neural Networks (for feature extraction)
- Principle Component Analysis

#### Image Processing
- colorspace conversion
- fast fourier transform
- frequency filtering
- Otsu Image Segmentation
- ORB keypoint and description
- Image resizing


### Designing your own processing blocks
There are two ways to create a block

#### 1) quick block creation
for operations that can be completed in a single function that
accepts one datum, you can create a block with a single line.
```python
import imagepypelines as ip

# create the function we use to process images
def normalize_image(img):
	return img / img.max()

# set up the block to work with grayscale and color imagery
io_map = {ip.ArrayType([None,None]):ip.ArrayType([None,None]),
			ip.ArrayType([None,None,3]):ip.ArrayType([None,None,3])}


block = ip.quick_block(normalize_image, io_map)
```

#### 2) object inheritance
_this is covered in more detail on our tutorial pages. this example will not cover training or label handling_
```python
import imagepypelines as ip

class NormalizeBlock(ip.SimpleBlock):
	"""normalize block between 0 and max_count, inclusive"""
	def __init__(self,max_count=1):
		self.max_count = max_count
		# set up the block to work with grayscale and color imagery
		io_map = {ip.ArrayType([None,None]):ip.ArrayType([None,None]),
					ip.ArrayType([None,None,3]):ip.ArrayType([None,None,3])}

		super(NormalizeBlock,self).__init__(io_map)

	def process(self,img):
		"""overload the processing function for this block"""
		return img.astype(np.float32) / img.max() * self.max_count
```

# Imaging Science Convenience Functions
In addition to the Pipeline, imagepypelines also contains convenience
utilities to accelerate the development of imaging science and computer vision
tasks


## Getting Standard Test Imagery
`imagepypelines` contains helper functions to quickly retrieve imagery that
are frequently used as benchmarks in the Imaging Science community
```python
import imagepypelines as ip
lenna = ip.lenna()
linear_gradient = ip.linear()
```
A full list of standard images can be retrieved with `ip.list_standard_images()`

for those of you in the Imaging Science program at RIT, there are a
couple easter eggs for ya ;)
```python
import imagepypelines as ip
ip.quick_image_view( ip.carlenna() )
ip.quick_image_view( ip.roger() )
ip.quick_image_view( ip.pig() )
```


## Viewing Imagery
Viewing imagery can be an surprisingly finicky process that differs machine
to machine or operating over X11. `imagepypelines` contains helper functions and objects for this purpose

### quick image viewer:

when you want to quickly display an image without any bells and whistles,
you can use the `quick_image_view` function

```python
import imagepypelines as ip
lenna = ip.lenna()

# Now lets display Lenna
ip.quick_image_view( lenna )

# display lenna normalized to 255
ip.quick_image_view(lenna, normalize_and_bin=True)
```

### Robust Image Viewer:

When you want a tool that can display multiple images at once, resize
images when desired and an optional frame_counter, you can use the `Viewer` object
```python
import imagepypelines as ip
import time

# lets build our Viewer and have it auto-resize images to 512x512
viewer = ip.Viewer('Window Title Here', size=(512,512))
# let's enable the frame counter, so we know what image we are on
viewer.enable_frame_counter()

# get all standard images
standard_images = ip.standard_image_gen()

# now let's display all images sequentially!
for img in standard_images:
	viewer.view( img )
	time.sleep(.1)
```

### Normalizing and binning an image
forgetting to do this gets ya more often than you might think when displaying
an image

```python
import imagepypelines as ip
import numpy as np
random_pattern = np.random.rand(512,512).astype(np.float32)

display_safe = ip.normalize_and_bin(random_pattern)
ip.Viewer().view(display_safe)
```
### Array Summarization
when debugging an image pipeline, printing out an image
can be counter productive. Imaging scientists frequently default
to printing out the shape or size of the data. `imagepypelines` contains
a helper class to quickly summarize an image in a formatted string
```python
import imagepypelines as ip
lenna = ip.lenna()

summary = ip.Summarizer(lenna)
print(summary)
```
produces the following
```
'[ARRAY SUMMARY | shape: (512, 512, 3) | size: 786432 | max: 255 | min: 3 | mean: 128.228 | dtype: uint8]'
```

### Image Coordinates
helper functions to get image coordinates quickly, useful if your
applications involve a mix of color and grayscale images.
Mostly useful to clean up code and avoid silly mistakes
```python
import imagepypelines as ip
lenna = ip.lenna()

# center pixel in the image
center_row, center_col = ip.centroid(lenna)

# number of rows and columns
rows, cols = ip.frame_size(lenna)

# shape and dtype
rows, cols, bands, dtype = ip.dimensions(lenna)
```

### Timing
Many imaging tasks are time sensitive or computationally
intensive. `imagepypelines` includes simple tools to time your process or function

#### Timer Objects
`imagepypelines` also includes a separate timer for timing things inside a function
or code block

##### absolute timing:
```python
from imagepypelines.util import Timer
import time

t = Timer()
time.sleep(5)
print( t.time(),"seconds" ) # or t.time_ms() for milliseconds
```

##### lap timing:
```python
from imagepypelines.util import Timer
import time

t = Timer()
for i in range(10):
	time.sleep(1)
	print( t.lap(),"seconds" ) # or t.lap_ms() for milliseconds
```

##### perform operation for N seconds:
```python
from imagepypelines.util import Timer
import time

def do_something():
	pass

# set the countdown
N = 10 #seconds
t = Timer()
t.countdown = N
while t.countdown:
	do_something()
```


#### timing Decorator
let's say we have a function that we think may be slowing down our pipeline.
We can add `@function_timer` on the line above the function
and see it automatically print how long the function took to run
```python
from imagepypelines.util import function_timer
from imagepypelines.util import function_timer_ms
import time

# add the decorator here
@function_timer
def we_can_time_in_seconds():
	time.sleep(1)

# we can also time the function in milliseconds using '@function_timer_ms'
@function_timer_ms
def or_in_milliseconds():
	time.sleep(1)

we_can_time_in_seconds()
or_in_milliseconds()
```
prints the following when the above code is run
```
(  function_timer  )[    INFO    ] ran function 'we_can_time_in_seconds' in 1.001sec
(  function_timer  )[    INFO    ] ran function 'or_in_milliseconds' in 1000.118ms
```

# Development Tools in `imagepypelines`
**_This section is for developers of `imagepypelines` or people who want `imagepypelines` closely integrated with their projects_**

## Printers
Are you a scientist???
If so, then you probably use millions of print statements to debug your code. (don't worry, we are all guilty of it)

`imagepypelines` encourages code traceability through the use of an object known as a **`Printer`**. Printers are objects that simply print out what's happening in a manner that's easy to read, color coded, and traceable to the object that is performing the current action. **Printers are extremely low overhead and will not affect the speed of your code more than a print statement.**

The functionality is similar to python's [`logging`](https://docs.python.org/3.7/library/logging.html) module

### making printers
printers can be created or retrieved using the `get_printer` function
```python
import imagepypelines as ip
printer = ip.get_printer('name your printer here')
```

### printer levels
printer messages can be filtered be priority so that only desired messages can be seen. In `imagepypelines`, printer levels are also color coded so they can be read easily in a console
```python
import imagepypelines as ip

example_printer = ip.get_printer('example!')
example_printer.debug('message') # prints 'message' at level 10 - blue text
example_printer.info('message') # prints 'message' at level 20 - white text
example_printer.warning('message') # prints 'message' at level 30 - yellow text
example_printer.comment('message') # prints 'message' at level 30 - green text
example_printer.error('message') # prints 'message' at level 40 - red text
example_printer.critical('message') # prints 'message' at level 50 - bold red text
```
Any level that is less than the current `GLOBAL_LOG_LEVEL` will **NOT** be printed. This makes it easy to filter out statements which may be erroneous or too numerous to make sense of.

this value can be set with the `set_global_printout_level` function
```python
import imagepypelines as ip
ip.set_global_printout_level('warning') # debug and info statements will not print now
```
local printer levels can be set with `Printer.set_log_level`
```python
import imagepypelines as ip
printer = ip.get_printer('Example Printer')
printer.set_log_level('error') # only error and critical functions will print
```

(this system is exactly the same as log_levels in python's [`logging`](https://docs.python.org/3.7/library/logging.html) module )

### disable or enabling certain printers
Sometimes you may only want to see printouts from a specific class or function. you can do this
with the `whitelist_printer`, `blacklist_printer`, or `disable_all_printers` functions

### default printer
there's a default printer in `imagepypelines` which is accessible through functions in the main module
```python
ip.debug('debug message') # level=10 --> (    imagepypelines    )[    DEBUG    ] debug message
ip.info('info message') # level=20 --> (    imagepypelines    )[    INFO    ] debug message
ip.warning('warning message') # level=30 --> (    imagepypelines    )[    WARNING    ] warning message
ip.error('error message') # level=40 --> (    imagepypelines    )[    ERROR    ] error message
ip.critical('critical message') # level=50 --> (    imagepypelines    )[    CRITICAL    ] critical message
ip.comment('comment message') # level=30 --> (    imagepypelines    )[    COMMENT    ] comment message
```

### class printers
a good strategy to encourage traceability is to create a printer object as a class instance attribute
```python
import imagepypelines as ip

class ExampleClass(object):
	def __init__(self,*args,**kwargs):
		name_of_class = self.__class__.__name__
		self.printer = ip.get_printer(name_of_class)
		self.printer.info("object instantiated!")

		self.do_something()

	def do_something(self):
		self.printer.warning("did something!")

ExampleClass()
```
produces the following
```
(   ExampleClass   )[    INFO    ] object instantiated!
(   ExampleClass   )[   WARNING  ] did something!
```
This way it's easy track what stage of the pipeline your code is in, because each object will have it's own printer and be distinguishable in the terminal!

## development decorators
`imagepypelines` contains four decorators that are made for use by developers in the backend

### @deprecated
made to decorate functions or classes that are deprecated
```python
import imagepypelines as ip

@ip.util.deprecated("'old_function' has been renamed to 'new_function'. references will be removed in a future version!")
def old_function():
	pass # real code will do something

old_function()
```

produces the following
```
(    imagepypelines    )[   WARNING  ] DEPRECIATION WARNING: 'old_function' has been renamed to 'new_function'. references will be removed in a future version!
```
### @experimental
made to decorate functions or classes that are experimental and may not be fully tested yet
```python
import imagepypelines as ip

@ip.util.experimental() # you can include a custom message here if you want
def new_feature():
	pass

new_feature()
```
produces the following
```
(    imagepypelines    )[   WARNING  ] EXPERIMENTAL WARNING: 'new_feature' is an experimental feature
```

### @human_test
This is a decorator made for unit tests which require a human to verify functionality. (for example: functions that display images)

**WARNING: unlike most decorators, this will not return the output of the wrapped function, but instead True or False.
This is because it is meant for Unit Tests, NOT actual use in a pipeline**
```python
import imagepypelines as ip
@ip.util.human_test
def unit_test_for_quick_image_view():
	ip.quick_image_view( ip.lenna() )

print('test succeeded ': unit_test_for_quick_image_view())
```
_lenna will display_

produces the following the terminal for the user to answer
```
did the test for 'unit_test_for_quick_image_view' succeed? Yes? No?
```


### @print_args
Decorator to print out the arguments a function is running with. Unlike other decorators described here, we encourage you to use this decorator frequently in your code during development to avoid silly mistakes
```python
import imagepypelines as ip
@ip.util.print_args
def func_with_lots_of_args(a, b, c=3, d=4):
			pass
func_with_lots_of_args(1, b=2, c='not 3')
```
produces the following in the terminal
```
(func_with_lots_of_args)[    INFO    ] running 'func_with_lots_of_args' with the following args:
        positional    | a : 1
        keyword       | b : 2
        keyword       | c : not 3
        default       | d : 4
```
