
Block IO Guide
==============

## The IoMap
Each block must include a user defined _IoMap_. An IoMap is an object that describes the inputs and outputs of a block. While not necessary for a block to be used in a pipeline, IoMaps greatly increase the traceability of your pipeline and allow `imagepypelines` to do a lot of the pesky debugging for you.

Every block has an IoMap saved to `block.io_map` which the pipeline will use to validate pipeline integrity and predict incompatible operations.

### Creating an IoMap
IoMaps can be created using a dictionary, where your keys are the type of your inputs and the values are the type of your outputs
```python
import imagepypelines as ip
mapping_dict = {
              ArrayType():ArrayType([None]),
              }
io_map = ip.IoMap(mapping_dict)
```

Inputs and outputs for a block can be viewed by printing the block's description
```python
import imagepypelines as ip
a = ip.blocks.Add(10)
print(a.description)
```
```
Add:1

adds a user-defined term to a numerical input

io mapping:
ArrayType(<arbitrary shape>) --> ArrayType(<arbitrary shape>) [same shape as input]
<class 'float'> --> <class 'float'>
<class 'int'> --> <class 'float'>
```


### ArrayTypes
blocks support strings, integers, floats and numpy arrays. However, numpy arrays must be specified using a special object: `ArrayType`

some examples are below:
```python
import imagepypelines as ip

# block takes and returns an input of 1D input of arbitrary length
io_map = ip.IoMap( {ArrayType([None]) : ArrayType([None])} )

# block needs a 2D input of (N,32) but returns a 1D (256,) array
io_map = ip.IoMap( {ArrayType([None,32]) : ArrayType([256])} )

# specify a block that takes in an image filename and returns a grayscale OR RGB image
io_map = ip.IoMap( {str : ArrayType([None,None],[None,None,3])} )

# block takes in an arbitrarily shaped array and returns an array of the same shape
io_map = ip.IoMap( {ip.ArrayType() : ip.Same()} )

# block takes in any numerical input and performs an operation on it
io_dict = {
            int : float, # make integers floats just to be safe
            float : float,
            ip.ARRAY_ND : ip.Same # take in any array and return the same shape
          }
io_map = ip.IoMap( io_dict )

# block takes in an image, saves it to disk and returns the filename
io_dict = {
            ip.GRAY : str, # ip.GRAY is equal to ip.ArrayType([None,None])
            ip.RGB : str, # ip.RGB is equal to ip.ArrayType([None,None,3])
          }
io_map = ip.IoMap( io_dict )
```

convenience variables for commonly used array types are preincluded and defined in: [quick_types](https://github.com/jmaggio14/imagepypelines/blob/develop/imagepypelines/core/quick_types.py)

## Example Block Creation
```python
# Let's create a block to divide an input by 1000
# this block will take in any numerical input
class Divide1000(object):
  def __init__(self):
    notes = "divides a numerical input by 1000"
    io_dict = {
                int : float,
                float : float,
                ip.ARRAY_ND : ip.Same,
              }
    super().__init__(io_dict, notes=notes)

  def process(self,datum):
    return datum / 1000.0
```
