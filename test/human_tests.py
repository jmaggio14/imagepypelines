import imsciutils as iu

@iu.human_test
def test_quick_image_view():
    """THIS TEST REQUIRES A HUMAN TO VIEW THE IMAGE"""
    import imsciutils as iu
    testing_printer = iu.get_printer('test_quick_image_view')

    pig = iu.pig()
    iu.quick_image_view(pig,'quick_image_view test')


@iu.human_test
def test_number_image():
    import imsciutils as iu
    testing_printer = iu.get_printer('test_number_image')

    pig = iu.pig()
    linear = iu.linear()

    num_pig = iu.number_image(pig,1)
    testing_printer.info("pig should be labeled '1'")
    num_linear = iu.number_image(linear,2)
    testing_printer.info("linear should be labeled '2'")

    iu.quick_image_view(pig,title='pig')
    testing_printer.info('PIG', iu.Summarizer(pig) )
    iu.quick_image_view(linear,title='linear')
    testing_printer.info('Linear', iu.Summarizer(linear) )
