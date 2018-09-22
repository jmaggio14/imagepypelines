import imsciutils as iu

# constants.py
def test_constants():
    testing_printer = iu.get_printer('test_constants')
    import imsciutils as iu
    if not 'CV2_INTERPOLATION_TYPES' in dir(iu):
        return False
    if not 'NUMPY_TYPES' in dir(iu):
        return False
    if not 'IMAGE_EXTENSIONS' in dir(iu):
        return False

    return True


# coordinates.py
def test_centroid():
    testing_printer = iu.get_printer('test_centroid')
    tester = iu.util.Tester(iu.centroid)
    lenna = iu.lenna()
    desired_output = (256,256)
    if not tester.exact_test(desired_output, lenna):
        return False

    return True


def test_frame_size():
    testing_printer = iu.get_printer('test_frame_size')
    tester = iu.util.Tester(iu.frame_size)
    lenna = iu.lenna()
    desired_output = tuple( lenna.shape[:2] )
    if not tester.exact_test(desired_output,lenna)
        return False

    return True


def test_dimensions():
    testing_printer = iu.get_printer('test_dimensions')
    tester = iu.Tester(iu.dimensions)
    lenna = iu.lenna()
    # tuple test
    desired_output = (lenna.shape[0],lenna.shape[1],lenna.shape[2],lenna.dtype)
    if not tester.exact_test(desired_output,lenna)
        return False
    # dimensions test
    desired_output = {
                        'rows':lenna.shape[0],
                        'cols':lenna.shape[1],
                        'bands':lenna.shape[2],
                        'dtype':lenna.dtype,
                        }
    if not tester.exact_test(desired_output,lenna)
        return False

    return True



# img_tools.py
def test_normalize_and_bin():
    testing_printer = iu.get_printer('test_normalize_and_bin')
    tester = iu.Tester(iu.normalize_and_bin)
    lenna = iu.lenna()
    desired_output= = np.uint8(lenna.astype(np.float32) / lenna.max() * 255)
    if not tester.exact_test(desired_output,lenna)
        return False

    return True










# END
