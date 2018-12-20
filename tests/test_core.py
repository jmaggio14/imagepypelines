from hypothesis import given, example
from hypothesis import strategies as st

import numpy as np
# =================== BaseBlock.py ===================
# ------------- ArrayType -------------
numpy_types = [np.uint8,
                np.int8,
                np.uint16,
                np.int16,
                np.int32,
                np.float32,
                np.float64,
                np.complex64,
                np.complex128]

# test function for ArrayType
@given( shape=st.lists(((st.integers(min_value=1, max_value=1000)))),
        dtypes=st.lists(st.sampled_from(numpy_types)) )
def test_ArrayType(shape, dtypes):
    """test ArrayType instantiation of multiple shapes and dtypes"""
    import imagepypelines as ip
    ip.ArrayType(shape,dtypes=dtypes)

# ------------- IoMap -------------
class TestIoMap(object):
    def test_reduction(self):
        """
        create an ArrayType with multiple shapes and see if the IoMap performs
        a proper breakdown
        ArrayType(shape1,shape2) --> ArrayType(shape1), ArrayType(shape2)
        """
        import imagepypelines as ip
        # create an Array Type with multiple shapes
        a = ip.ArrayType([None,None,None],[None,None],[None])
        b = ip.ArrayType([None,None,None,None],[None,None])
        io_map = ip.IoMap( {a:b} )
        assert len(io_map.inputs) == len(io_map.outputs) == 6

    def test_output_given_input(self):
        """
        check that the block io mapping system is operating correctly
        """
        import imagepypelines as ip

        a = ip.ArrayType([None,None,None],[None,None],[None])
        b = ip.ArrayType([None],[None,None])
        io_map = ip.IoMap( {a:b} )

        desired_output = ip.ArrayType([None]), ip.ArrayType([None,None])
        given_output = io_map.output_given_input(ip.ArrayType([None]))

        assert set(desired_output) == set(given_output)

    # JM: TODO: add dtype checking

# =================== block_subclasses.py ===================
class TestSimpleBlock(object):
    """
    Create a test SimpleBlock and run some data through it
    """
    def test_block_creation_and_processing(self):
        import imagepypelines as ip
        # create a test block via object inheritance
        class AddOne(ip.SimpleBlock):
            def __init__(self):
                io_map = {ip.ArrayType([None]):ip.ArrayType([None])}
                super(AddOne,self).__init__(io_map)

            def process(self, datum):
                return datum + 1

        block = AddOne()
        input_datum = np.zeros( (512,) )

        processed = block._pipeline_process([input_datum])

        assert np.all( np.around(processed[0],1) == 1.0 )


class TestBatchBlock(object):
    """
    Create a test BatchBlock and run some data through it
    """
    def test_block_creation_and_processing(self):
        import imagepypelines as ip
        # create a test block via object inheritance
        class AddOne(ip.BatchBlock):
            def __init__(self):
                io_map = {ip.ArrayType([None]):ip.ArrayType([None])}
                super(AddOne,self).__init__(io_map)

            def batch_process(self, data):
                for i in range( len(data) ):
                    data[i] = data[i] + 1
                return data

        block = AddOne()
        input_datum = np.zeros( (512,) )
        (proc1,proc2),_ = block._pipeline_process([input_datum,input_datum])

        assert np.all( np.around(proc1,1) == 1.0 )
        assert np.all( np.around(proc2,1) == 1.0 )


class TestTfBlock(object):
    """
    Create a test TfBlock and run some data through it
    """
    def test_block_creation_and_processing(self):
        import imagepypelines as ip
        import tensorflow as tf
        # create a test block via object inheritance
        class AddOne(ip.TfBlock):
            def __init__(self):
                io_map = {ip.ArrayType([None]):ip.ArrayType([None])}
                super(AddOne,self).__init__(io_map)

            def setup_graph(self,data_placeholder,label_placeholder):
                one = tf.constant(1.0,tf.float32)
                processed = tf.math.add(data_placeholder,one,name='processed')
                return processed.name

        block = AddOne()
        input_datum = np.zeros( (512,) )
        data = [input_datum,input_datum]
        labels = [0,1]
        (proc1,proc2),lbls = block._pipeline_process(data,labels)

        assert labels == lbls, "label fetching failed"
        assert np.all( np.around(proc1,1) == 1.0 )
        assert np.all( np.around(proc2,1) == 1.0 )

        # TEMP COMMENT 12/11/18 uncomment ASAP
        # try to save and restore the pipeline
        # pipeline = ip.Pipeline([block])
        # pipeline_hash = hash(pipeline)
        #
        # restored_pipeline = ip.restore_from_file( pipeline.save() )
        # assert hash(restored_pipeline) == pipeline_hash


# =================== caching.py ===================
# JM: @Ryan, I'm leaving this blank for you to populate



# =================== constants.py ===================
def test_constants():
    import imagepypelines as ip
    assert 'CV2_INTERPOLATION_TYPES' in dir(ip)
    assert 'NUMPY_TYPES' in dir(ip)
    assert 'IMAGE_EXTENSIONS' in dir(ip)
    assert 'PRETRAINED_NETWORKS' in dir(ip)


# =================== error_checking.py ===================
# TODO - JM

# =================== Exceptions.py ===================
# TODO - JM

# =================== filters.py ===================
# TODO - JM

# =================== img_tools.py ===================
# TODO - JM

# =================== imports.py ===================
class TestImports(object):
    def test_opencv(self):
        import imagepypelines as ip
        import cv2
        assert cv2 == ip.import_opencv()

    def test_tensorflow(self):
        import imagepypelines as ip
        import tensorflow as tf
        assert tf == ip.import_tensorflow()

# =================== ml_tools.py ===================
def test_accuracy():
    import imagepypelines as ip
    predicted =    [0,1,0,1,0,1,0,1,0,1]
    ground_truth = [1,1,1,1,1,1,1,1,1,1]
    # we should have 50% accuracy
    accuracy = round(ip.accuracy(predicted,ground_truth),3)
    assert accuracy == .5


# class TestSample(object):
#     def test_xsample(self):
#         """confirm that xsample returns a uniform sample by confirming the null
#         hypothesis
#         """
#         import imagepypelines as ip
#         import numpy as np
#
#         alpha = 1e-3 # null hypothesis cutoff
#         # create a random uniform distribution min = 0, max = 1
#         uni = [x for x in np.random.uniform(0,1,1000)]
#
#         if p < alpha:


def test_chunk():
    import imagepypelines as ip
    size = 901
    n = 10
    example = list( range(size) )
    # we should have 9 lists of length 91, and one of length 82
    chunks = ip.chunk(example,n)

    assert all( len(x) == 91 for x in chunks[:len(chunks)-1])
    assert len(chunks[-1]) == 82


def test_batch():
    import imagepypelines as ip
    size = 901
    n = 91
    example = list( range(size) )
    # we should have 9 lists of length 91, and one of length 82
    batches = ip.batch(example,n)

    assert all( len(x) == 91 for x in batches[:len(batches)-1])
    assert len(batches[-1]) == 82


def test_chunks2list():
    import imagepypelines as ip
    import copy
    ls = list(range(1000))
    ls2 = copy.deepcopy(ls)
    chunks = ip.chunk(ls, 10)
    assert ls == ip.chunks2list(chunks)

def test_xsample():
    import imagepypelines as ip
    fraction = 0.05

    population = list( range(100) )

    sample = ip.xsample(population,fraction)

def test_xysample():
    import imagepypelines as ip
    import copy
    fraction = 0.05

    population = list( range(100) )
    pop_labels = copy.deepcopy(population)

    sample,lbls = ip.xysample(population,pop_labels,fraction)

    # check to make sure corresponding labels are returned for the data
    assert len(sample) == len(lbls)
    assert all(sample[i] == lbls[i] for i in range(len(sample)))
    assert len(samples) == int(fraction * len(population))



# =================== pipeline_tools.py ===================
# TODO - JM

# =================== Pipeline.py ===================
# TODO - JM

# =================== Printer.py ===================
# TODO - JM

# =================== quick_types.py ===================
def test_quick_types():
    import imagepypelines as ip
    assert hasattr(ip,'GRAY')
    assert hasattr(ip,'RGB')
    assert ip.GRAY == ip.ArrayType([None,None])
    assert ip.RGB == ip.ArrayType([None,None,3])

# =================== standard_image.py ===================
# a lot of tests simplY run the function to verify there are no errors
# they do not all check outputs due to the dynamic nature of the standard image set

class TestStandardImages(object):
    def test_list_standard_images(self):
        import imagepypelines as ip
        ip.list_standard_images()

    def test_standard_image_filenames(self):
        import imagepypelines as ip
        import os
        fnames = ip.standard_image_filenames()
        assert all(os.path.exists(f) for f in fnames),\
            "not all standard images filenames exist"

    def test_standard_image_gen(self):
        import imagepypelines as ip
        import types
        std_images = ip.standard_image_gen()
        assert isinstance(std_images,types.GeneratorType)

    def test_standard_images(self):
        import imagepypelines as ip
        std_images = ip.standard_images()
        assert isinstance(std_images,list)

    def test_get_standard_image(self):
        import imagepypelines as ip
        import numpy as np
        # test known filenames
        fnames = ip.list_standard_images()
        assert all(isinstance(ip.get_standard_image(f),np.ndarray) for f in fnames)
        # test known non-existant filename
        import uuid
        fname = uuid.uuid4().hex # create random file string
        try:
            ip.get_standard_image(fname)
        except ValueError:
            pass






# =================== Viewer.py ===================
# TODO - JM
