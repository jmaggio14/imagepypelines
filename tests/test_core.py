from hypothesis import given, example
from hypothesis import strategies as st

import numpy as np
# =================== Block.py ===================
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
@given( shape=st.lists(((st.integers(min_value=1, max_value=1000)))) )
def test_ArrayType(shape):
    """test ArrayType instantiation of multiple shapes and dtypes"""
    import imagepypelines as ip
    ip.ArrayType(shape)

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

    def test_output(self):
        """
        check that the block io mapping system is operating correctly
        """
        import imagepypelines as ip

        a = ip.ArrayType([None,None,None],[None,None],[None])
        b = ip.ArrayType([None],[None,None])
        io_map = ip.IoMap( {a:b} )

        desired_output = ip.ArrayType([None]), ip.ArrayType([None,None])
        given_output = io_map.output( (ip.ArrayType([None]),) )

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


# class TestTfBlock(object):
#     """
#     Create a test TfBlock and run some data through it
#     """
#     def test_block_creation_and_processing(self):
#         import imagepypelines as ip
#         import tensorflow as tf
#         # create a test block via object inheritance
#         class AddOne(ip.TfBlock):
#             def __init__(self):
#                 io_map = {ip.ArrayType([None]):ip.ArrayType([None])}
#                 super(AddOne,self).__init__(io_map)
#
#             def setup_graph(self,data_placeholder,label_placeholder):
#                 one = tf.constant(1.0,tf.float32)
#                 processed = tf.math.add(data_placeholder,one,name='processed')
#                 return processed.name
#
#         block = AddOne()
#         input_datum = np.zeros( (512,) )
#         data = [input_datum,input_datum]
#         labels = [0,1]
#         (proc1,proc2),lbls = block._pipeline_process(data,labels)
#
#         assert labels == lbls, "label fetching failed"
#         assert np.all( np.around(proc1,1) == 1.0 )
#         assert np.all( np.around(proc2,1) == 1.0 )
#
#         # TEMP COMMENT 12/11/18 uncomment ASAP
#         # try to save and restore the pipeline
#         # pipeline = ip.Pipeline([block])
#         # pipeline_hash = hash(pipeline)
#         #
#         # restored_pipeline = ip.restore_from_file( pipeline.save() )
#         # assert hash(restored_pipeline) == pipeline_hash


# =================== caching.py ===================
# JM: @Ryan, I'm leaving this blank for you to populate
# def test_cache_encryption():

def test_list_cache_filenames():
    import imagepypelines as ip
    if not ip.cache.enabled():
        ip.cache.secure_enable()

    fnames = ip.cache.list_filenames()

class TestCacheErrorss():
    # test illegal chars
    def test_illegal_chars(self):
        import imagepypelines as ip
        if not ip.cache.enabled():
            ip.cache.secure_enable()

        fail = True
        try:
            ip.cache['this/is/illegal'] = "this is illegal"
        except ValueError:
            fail = False

        if fail:
            raise RuntimeError

    def test_nonstring(self):
        import imagepypelines as ip
        if not ip.cache.enabled():
            ip.cache.secure_enable()

        fail = True
        try:
            ip.cache[5324] = "this is illegal"
        except TypeError:
            fail = False

        if fail:
            raise RuntimeError

    def test_nokey(self):
        import imagepypelines as ip
        if not ip.cache.enabled():
            ip.cache.secure_enable()

        fail = True
        try:
            a = ip.cache['this is not a key']
        except KeyError:
            fail = False

        if fail:
            raise RuntimeError

    def test_wrong_pass(self):
        import imagepypelines as ip
        if not ip.cache.enabled():
            ip.cache.secure_enable('sdadafdas')

        ip.cache['key'] =1

        fail = True
        try:
            ip.cache.load('key', passwd="NOT RIGHT")
        except ip.Exceptions.CachingError:
            fail = False

        if fail:
            raise RuntimeError


def test_cache_dir_deletion():
    import imagepypelines as ip
    import os
    if not ip.cache.enabled():
        ip.cache.secure_enable()

    os.makedirs( os.path.join(ip.cache.subdir, 'testdir') )
    ip.cache.purge()

def test_cache_iter():
    import imagepypelines as ip
    if not ip.cache.enabled():
        ip.cache.secure_enable()

    ip.cache.purge()
    ip.cache['test1'] = 'test1'
    ip.cache['test2'] = 'test2'
    ip.cache['test3'] = 'test3'

    items = list(x for x in ip.cache)
    assert sorted(items) == sorted(['test1','test2','test3'])
    ip.cache.purge()


def test_cache_repr():
    import imagepypelines as ip
    repr(ip.cache)

def test_cache_passgen():
    import imagepypelines as ip
    ip.cache.passgen()
    
# =================== constants.py ===================
def test_constants():
    import imagepypelines as ip
    assert 'CV2_INTERPOLATION_TYPES' in dir(ip)
    assert 'NUMPY_TYPES' in dir(ip)
    assert 'IMAGE_EXTENSIONS' in dir(ip)
    assert 'PRETRAINED_NETWORKS' in dir(ip)


# =================== error_checking.py ===================
def test_interpolation_type_check():
    import imagepypelines as ip
    import cv2

    for inter in ip.CV2_INTERPOLATION_TYPES:
        ip.interpolation_type_check(inter)


    failure = -1
    try:
        ip.interpolation_type_check(failure)
    except ip.InvalidInterpolationType:
        pass

def test_dtype_type_check():
    import imagepypelines as ip
    import numpy as np

    # success
    for dtype in ip.NUMPY_TYPES:
        ip.dtype_type_check(dtype)

    # failure
    try:
        ip.dtype_type_check(-1)
    except ip.InvalidNumpyType:
        pass
    else:
        raise RuntimeError("failure failed")

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
    n = 10.0
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

    assert all( len(x) == 91 for x in batches[:-1])
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
    assert len(sample) == int(fraction * len(population))



# =================== pipeline_tools.py ===================
# def test_quick_block():
#     import imagepypelines as ip
#     import numpy as np
#
#     io_map = {ip.GRAY:ip.GRAY}
#     process_fn = lambda x : x+1
#     name = "this is a test"
#
#     # try a block with a custom name
#     plus_one_block = ip.quick_block(process_fn,io_map,name)
#
#     assert isinstance(plus_one_block,ip.Block)
#     assert plus_one_block.name == name + ':1'
#
#     pipeline = ip.Pipeline([plus_one_block])
#     processed = pipeline.process([np.zeros((512,512),dtype=np.uint8)])
#     assert np.all(np.around(processed,3) == 1)
#
#     # try a block with a generated name
#     plus_one_block = ip.quick_block(process_fn,io_map)
#
#     assert isinstance(plus_one_block,ip.Block)
#     assert plus_one_block.name == '<lambda>' + ':1'
#
#     pipeline = ip.Pipeline([plus_one_block])
#     processed = pipeline.process([np.zeros((512,512),dtype=np.uint8)])
#     assert np.all(np.around(processed,3) == 1)










# =================== Pipeline.py ===================
# RH - Taking this guy over Jiff
# JM - Unfortunately had to temporarily comment this out to get website to build
# class TestPipeline(object):
#     def test_list_methods(self):
#         import imagepypelines as ip
#
#         # All of this can be cleaned up. Want to have graceful failure too!!!
#
#         C2G = ip.builtin_blocks.Color2Gray
#         FFT = ip.builtin_blocks.FFT
#         IFFT = ip.builtin_blocks.IFFT
#
#         P = ip.Pipeline([C2G(),FFT(),IFFT()],name='Arbitrary')
#
#         P.debug()
#
#         P.add(FFT())
#         P_copy = P.copy()
#         P_copy.rename('Arbitrary_copy')
#
#         P.insert(2,FFT())
#         P.insert(12,C2G())
#         P.insert('a',IFFT())
#         P.remove(P.names[2])
#         P.remove(12)
#         P.clear()
#         P.join(ip.Pipeline([C2G(),FFT()],name='Arbitrary2'))
#         P.join(FFT())
#         P.join(ip.Pipeline([12,'a']),name=float(12))
#
#         sstr = repr(P)
#         outstr = str(P)
#         it = iter(P)
#         nxt = next(P)
#
#         names = P_copy.names
#         trained = P_copy.trained
#         req_labels = P_copy.requires_labels
#
#         P[2] = 12
#         P[2] = FFT()
#         blk = P[-1]
#
#         del P_copy[2]
#
#         del P_copy

# =================== Logger.py ===================
# TODO - JM

# =================== quick_types.py ===================
# def test_quick_types():
#     import imagepypelines as ip
#     assert hasattr(ip,'GRAY')
#     assert hasattr(ip,'RGB')
#     assert ip.GRAY == ip.ArrayType([None,None])
#     assert ip.RGB == ip.ArrayType([None,None,3])

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
