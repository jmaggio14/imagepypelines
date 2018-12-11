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
        assert len(io_map.inputs) == 6
        assert len(io_map.outputs) == 6

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
    Create a test BatchBlock and run some data through it
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

        # try to save and restore the pipeline
        pipeline = ip.Pipeline([block])
        pipeline_hash = hash(pipeline)

        restored_pipeline = ip.restore_from_file( pipeline.save() )
        assert hash(restored_pipeline) == pipeline_hash


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
# TODO - JM

# =================== pipeline_tools.py ===================
# TODO - JM

# =================== Pipeline.py ===================
# TODO - JM

# =================== Printer.py ===================
# TODO - JM

# =================== quick_types.py ===================
# TODO - JM

# =================== standard_image.py ===================
# TODO - JM

# =================== Viewer.py ===================
# TODO - JM
