# imsciutils
This is a repo of code that we seem to find ourselves using in projects in many academic, personal, and corporate settings. It is not made for any specific purpose, and is meant to act in an accessory role programmatic manipulation and processing of imagery.

We are imaging scientists, and as such the code in this repo will be skewed towards imaging tasks.

## Compatibility
python 3.5+ (python 2.7 backwards)

Module Dependencies
-------------------
- numpy
- matplotlib
- scipy
- keras
- scikit-learn
- termcolor
- opencv3
- Pillow
- colorama (on windows)
- Sphinx (for autodocumentation)

Install Dependencies
```
pip install numpy matplotlib opencv-python scipy kera scikit-learn termcolor Pillow colorama Sphinx --user
```

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

### Timing
Many imaging tasks are time sensitive or computationally
intensive. `imsciutils` includes simple tools to time your process or function

#### timing Decorator
let's say we have a function that we think may be slowing down our pipeline.
We can add `@function_timer` on the line above the function
and see it automatically print how long the function took to run
```python
from imsciutils.util import function_timer
from imsciutils.util import function_timer_ms
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

#### Timer Objects
`imsciutils` also includes a separate timer for timing things inside a function
or code block
```python
from imsciutils.util import Timer
import time

t = Timer()
for i in range(2):
	time.sleep(1)
	print(i,") t.lap() resets every time it's called:", t.lap() ) # we can call the 'lap' function to get lap timing
	print(i,') t.time() counts up always: ', t.time() ) # or the 'time' to get the total time
```
produces the following
```
0 ) t.lap() resets every time it's called: 1.0
0 ) t.time() counts up always:  1.001
1 ) t.lap() resets every time it's called: 1.002
1 ) t.time() counts up always:  2.003
```


# HIGHER LEVEL FUNCTIONALITY
`imsciutils` also contains objects for more specific, higher level tasks
such as talking to a webcam, writing videos and images, extact image features
using pretrained neural networks, etc.

**_The following examples may be longer and contain psuedocode_**

**_It may be necessary to look at docstrings to fully realize the capabilities of the objects presented_**

## Machine learning


### Pretrained Network Feature Extraction
There is a convenience wrapper around keras built into `imsciutils`
to extract image features using pretrained networks
```python
import imsciutils as iu
network = iu.ml.FeatureExtractor('resnet50', pooling_type='avg')

# it works with single images
lenna = iu.lenna()
lenna_features = network.extract_features(lenna)

# it also works with a list of images
img_batch = [iu.lenna(), iu.pig(), iu.crowd()]
batch_features = network.extract_features(img_batch)

# it even works with filenames
filenames = ['path/to/lenna.tiff','path/to/pig.jpg','path/to/crowd.jpg']
img_features = network.extract_features(filenames)
```

### Configuration Factory
In many machine learning applications, parameters have to
be tweaked frequently to optimize a model. This can be a tedious task
and frequently involves a human tweaking configurations files. This
object is meant to simplify that process by **generating config permutations
from a sample of arguments and keyword arguments**

#### simple example
```python
import imsciutils as iu
from imsciutils.util import ConfigFactory

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

config_factory = ConfigFactory(*arg_trials,**kwarg_trials)
for args,kwargs in config_factory:
	run_important_test(*args,**kwargs)
```
#### real world example
let's say we are training a DNN classifier and we want to test



# Development Tools in `imsciutils`
**_This section is for developers of `imsciutils` or people who want `imsciutils` closely integrated with their projects_**

## Printers
Are you a scientist???
If so, then you probably use millions of print statements to debug your code. (don't worry, we are all guilty of it)

`imsciutils` encourages code traceability through the use of an object known as a **`Printer`**. Printers are objects that simply print out what's happening in a manner that's easy to read, color coded, and traceable to the object that is performing the current action. **Printers are extremely low overhead and will not affect the speed of your code more than a print statement.**

The functionality is similar to python's [`logging`](https://docs.python.org/3.7/library/logging.html) module

### making printers
printers can be created or retrieved using the `get_printer` function
```python
import imsciutils as iu
printer = iu.get_printer('name your printer here')
```

### printer levels
printer messages can be filtered be priority so that only desired messages can be seen. In `imsciutils`, printer levels are also color coded so they can be read easily in a console
```python
import imsciutils as iu

example_printer = iu.get_printer('example!')
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
import imsciutils as iu
iu.set_global_printout_level('warning') # debug and info statements will not print now
```
local printer levels can be set with `Printer.set_log_level`
```python
import imsciutils as iu
printer = iu.get_printer('Example Printer')
printer.set_log_level('error') # only error and critical functions will print
```




(this system is exactly the same as log_levels in python's [`logging`](https://docs.python.org/3.7/library/logging.html) module )

### default printer
there's a default printer in `imsciutils` which is accessible through functions in the main module
```python
iu.debug('debug message') # level=10 --> (    imsciutils    )[    DEBUG    ] debug message
iu.info('info message') # level=20 --> (    imsciutils    )[    INFO    ] debug message
iu.warning('warning message') # level=30 --> (    imsciutils    )[    WARNING    ] warning message
iu.error('error message') # level=40 --> (    imsciutils    )[    ERROR    ] error message
iu.critical('critical message') # level=50 --> (    imsciutils    )[    CRITICAL    ] critical message
iu.comment('comment message') # level=30 --> (    imsciutils    )[    COMMENT    ] comment message
```

### class printers
a good strategy to encourage traceability is to create a printer object as a class instance attribute
```python
import imsciutils as iu

class ExampleClass(object):
	def __init__(self,*args,**kwargs):
		name_of_class = self.__class__.__name__
		self.printer = iu.get_printer(name_of_class)
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
`imsciutils` contains four decorators that are made for use by developers in the backend

### @depreciated
made to decorate functions or classes that are depreciated
```python
import imsciutils as iu

@iu.depreciated("'old_function' has been renamed to 'new_function'. references will be removed in a future version!")
def old_function():
	pass # real code will do something

old_function()
```

produces the following
```
(    imsciutils    )[   WARNING  ] DEPRECIATION WARNING: 'old_function' has been renamed to 'new_function'. references will be removed in a future version!
```
### @experimental
made to decorate functions or classes that are experimental and may not be fully tested yet
```python
import imsciutils as iu

@iu.experimental() # you can include a custom message here if you want
def new_feature():
	pass

new_feature()
```
produces the following
```
(    imsciutils    )[   WARNING  ] EXPERIMENTAL WARNING: 'new_feature' is an experimental feature
```

### @human_test
This is a decorator made for unit tests which require a human to verify functionality. (for example: functions that display images)

**WARNING: unlike most decorators, this will not return the output of the wrapped function, but instead True or False.
This is because it is meant for Unit Tests, NOT actual use in a pipeline**
```python
import imsciutils as iu
@iu.human_test
def unit_test_for_quick_image_view():
	iu.quick_image_view( iu.lenna() )

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
import imsciutils as iu
@iu.print_args
def func_with_lots_of_args(a, b, c=3, d=4):
			pass
func_with_lots_of_args(1, b=2, c='not 3')
```
produces the following in the terminal
```
(    imsciutils    )[    INFO    ] running 'func_with_lots_of_args' with the following args:

            type    | arg_name |  value
        ==================================================
        (  positional  ) a : 1
        (   keyword    ) b : 2
        (   keyword    ) c : not 3
        (   default    ) d : 4
```
