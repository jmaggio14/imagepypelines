# imsciutils
This is a repo of code that we seem to find ourselves using in projects in many academic, personal, and corporate settings. It is not made for any specific purpose, and is meant to act in an accessory role programmatic manipulation and processing of imagery.

We are imaging scientists, and as such the code in this repo will be skewed towards imaging tasks.

## Compatibility
python 3.5+ (python 2.7 backwards)

Module Dependencies
-------------------
- numpy
- matplotlib
- opencv
- scipy
- keras
- scikit-*
- termcolor

## Documentation
There is autodoc sphinx documentation with this project, following the google docstrings format. To build / view these docs on windows::

	docs\make.bat html

And on every other platform::

	cd docs && make html

Then the html documentation will be available at docs/build/html/index.html
_____________________________

# BASIC HOW TOs
## Getting Standard Test Imagery
`imsciutils` contains helper functions to quickly retrieve imagery that
are frequently used as benchmarks in the Imaging Science community
```python
import imsciutils as iu
lenna = iu.lenna()
linear_gradient = iu.linear()
```
A full list of standard images can be retrieved with `iu.list_standard_images()`

for those of you in the Imaging Science program at RIT, there are a
couple easter eggs for ya ;)
```python
import imsciutils as iu
iu.quick_image_view( iu.carlenna() )
iu.quick_image_view( iu.roger() )
iu.quick_image_view( iu.pig() )
```


## Viewing Imagery
Viewing imagery can be an surprisingly finicky process that differs machine
to machine or operating over X11. `imsciutils` contains helper functions and objects for this purpose

### quick image viewer:

when you want to quickly display an image without any bells and whistles,
you can use the `quick_image_view` function

```python
import imsciutils as iu
lenna = iu.lenna()

# Now lets display Lenna
iu.quick_image_view( lenna )

# display lenna normalized to 255
iu.quick_image_view(lenna, normalize_and_bin=True)
```

### Robust Image Viewer:

When you want a tool that can display multiple images at once, resize
images when desired and an optional frame_counter, you can use the `Viewer` object
```python
import imsciutils as iu
import time

# lets build our Viewer and have it auto-resize images to 512x512
viewer = iu.Viewer('Window Title Here', size=(512,512))

# get all standard images
standard_images = iu.standard_image_gen()

# now let's display all images sequentially!
for img in standard_images:
	viewer.view( img )
	time.sleep(1)
```

### Normalizing and binning an image
forgetting to do this gets ya more often than you might think when displaying
an image

```python
import imsciutils as iu
import numpy as np
random_pattern = np.random.rand(512,512).astype(np.float32)

display_safe = iu.normalize_and_bin(random_pattern)
iu.Viewer().view(display_safe)
```
### Array Summarization
when debugging an image pipeline, printing out an image
can be counter productive. Imaging scientists frequently default
to printing out the shape or size of the data. `imsciutils` contains
a helper class to quickly summarize an image in formated string
```python
import imsciutils as iu
lenna = iu.lenna()

summary = iu.Summarizer(lenna)
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
import imsciutils as iu
lenna = iu.lenna()

# center pixel in the image
center_row, center_col = iu.centroid(lenna)

# number of rows and columns
rows, cols = iu.frame_size(lenna)

# shape and dtype
rows, cols, bands, dtype = iu.dimensions(lenna)
```




# HIGHER LEVEL FUNCTIONALITY
`imsciutils` also contains objects for more specific, higher level tasks
such as talking to a webcam, writing videos and images, extact image features
using pretrained neural networks, etc.

**_The following examples may be longer and contain psuedocode_**

**_It may be necessary to look at docstrings to fully realize the capabilities of the objects presented_**

## Machine learning

### Configuration Permuter
In many machine learning applications, parameters have to
be tweaked frequently to optimize a model. This can be a tedious task
and frequently involves a human tweaking configurations files. This
object is meant to simplify that process by generating permutations
from a sample of arguments and keyword arguments

```python
# Warning, the next two lines are psuedocode
def run_important_test(arg1,arg2,arg3,first,second,third):
	do_something_important()


arg_trials = [0, # the first positional will always be 0 in all permutations
	['a','b','c'], # trials for second positional arguments
	['u','w','x','y','z'], # trials for third positional argument
	]

kwarg_trials = {'first':None, # this keyword will always be None in all permutations
	'second':['I','J','K'], # trials for 'first' keyword argument
	'third':['i','j','k'], # trials for 'first' keyword argument
	}

permuter = Permuter(*arg_trials,**kwarg_trials)
for args,kwargs in permuter:
	run_important_test(*args,**kwargs)
```

### Pretrained Network Feature Extraction
There is a convenience wrapper around keras built into `imsciutils`
to extract image features using pretrained networks
```python
import imsciutils as iu
network = iu.ml.FeatureExtractor('resnet50',pooling_type='avg')

# it works with single images
lenna = iu.lenna()
lenna_features = network.extract_features(lenna)

# it also works with a list of images
img_batch = [iu.lenna(),iu.pig(),iu.crowd()]
batch_features = network.extract_features(img_batch)

# it even works with filenames so you can process images directly off the disk!
filenames = ['path/to/lenna.tiff','path/to/pig.jpg','path/to/crowd.jpg']
img_features = network.extract_features(filenames)
```
