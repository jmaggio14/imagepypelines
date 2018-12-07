from hypothesis import given, example
from hypothesis import strategies as st
import numpy as np
# =================== BaseBlock.py ===================
# ------------- ArrayType -------------
# create function to generate shape and dtype for ArrayType Creation
@st.composite
def shape_and_dtype(draw):
    shape_elements = strategy([one_of((integers_in_range(0, 1000),
                                None,
                                floats_in_range(0, 1000)))])

    numpy_types = (np.uint8, np.int8, np.uint16, np.int16, np.int32,
                    np.float32, np.float64, np.complex64, np.complex128)
    shape = draw(shape_elements)
    dtypes = draw( st.lists(numpy_types) )
    return shape, dtypes

# test function for ArrayType
@given(shape_and_dtype())
@example(shape=[])
def test_ArrayType(shape,dtypes):
    import imagepypelines as ip
    # test instantiation of multiple shapes and dtypes
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
        a = ArrayType([None,None,None],[None,None],[None])
        b = ArrayType([None,None,None,None],[None,None])
        io_map = ip.IoMap( {a:b} )
        assert len(io_map.inputs) == 3
        assert len(io_map.outputs) == 2

    def test_output_given_input(self):
        """
        check that the block io mapping system is operating correctly
        """
        import imagepypelines as ip

        a = ArrayType([None,None,None],[None,None],[None])
        b = ArrayType([None,None,None,None],[None,None])
        io_map = ip.IoMap( {a:b} )

        desired_output = io_map.reduce(b)
        given_output = io_map.output_given_input(ArrayType([None]))

        assert sorted(set(desired_output),set(given_output))

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
                data = np.stack(data,axis=1)
                return [np.squeeze(d) for d in np.vsplit(data+1,len(data))]

        block = AddOne()
        input_datum = np.zeros( (512,) )

        processed = block._pipeline_process([input_datum,input_datum])

        assert np.all( np.around(processed[0],1) == 1.0 )
        assert np.all( np.around(processed[1],1) == 1.0 )

# =================== constants.py ===================
def test_constants():
    import imagepypelines as ip
    assert 'CV2_INTERPOLATION_TYPES' in dir(ip)
    assert 'NUMPY_TYPES' in dir(ip)
    assert 'IMAGE_EXTENSIONS' in dir(ip)
    assert 'PRETRAINED_NETWORKS' in dir(ip)
