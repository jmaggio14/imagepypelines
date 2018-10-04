# Priorities!
- [ ] Pause Development and work on Unit Tests!

## stuff we'll have to write from scratch
- [ ] multispectral image reading - formats?
- [ ] multispectral image writing - formats?
- [ ] quick plotting tools
- [ ] blackbody eq
- [ ] stuff to easily bind c code (to load in a DLL or .so) - Nate?
- [ ] autogenerate file names

### sensor tools???? --- Ryan do you have this stuff?

### machine learning section
- [ ] thundersvm classifer
- [ ] dimensionality reducer - Jeff
- [ ] ORB, SIFT - Jeff
- [ ] Fisher Vectors
- [x] keras pretrained wrapper
- [ ] load in images into classes (auto-labelling)

### Ryan Senior stuff
- [ ] bag of words stuff

### non-imaging stuff
- [x] timers - Jeff
- [x] logging tools
- [ ] retry on fail
- [x] add ansi codes to text - Jeff
- [x] prevent_overwrite() - Jeff
- [x] Writing a series of images on the fly
- [x] Camera Capture
- [ ] Image Buffer
- [ ] Auto Grapher

## stuff from ipcv (may need to rewrite to optimize)
- [x] dimensions
- [ ] frequency filtering (maybe this is too close to home)
- [ ] histogram enhancement
- [ ] probably some segmentation algorithms
- [ ] affine transforms
- [x] normalization - Nate?
- [ ] clipping - Nate?

# other shit
- [x] standard test images in a repo - Jeff
- [x] MNIST, Lenna, - Jeff
- [x] standard image wrapper - Jeff
- [ ] add text to image wrapper (cv2.putText sucks I'm sorry)
- [ ] unit tests? lots of functionality was broken by recent restructure
- [x] documentation - ongoing
- [ ] remote webcam?
- [ ] slit-scan tool - Nate

# Standard Image
- [ ] get giza
- [ ] get checkerboard

# Image Viewer
- [x] frame counter - Jeff
- [ ] get ROI - Ryan
- [ ] auto-normalize - Ryan - ND: I wrote some normalization functions
- [ ] Separate Window interaction class - Ryan
- [ ] auto image stitcher (something that will resize images automatically)
- [ ] plugin system - Nate?


# Pipelining system
## builtin blocks
- SIFT
- ORB
- Pretrained NN
- Fisher Vectors
- Ryan's Summary thingy
- histogram
- quantization
## utility
- Image loader
- Resize
- reshaper
- normalize
