import numpy as np



def test_Pipeline():
    import imagepypelines as ip
    # ###############################################################################
    #                                 General Testing
    # ###############################################################################
    # Blockify testing
    @ip.blockify( types={'a':int, 'b':int}, kwargs=dict(value=10) )
    def add_val(a,b,value):
        return a+value, b+value

    @ip.blockify( types={'a':int, 'b':int}, kwargs=dict(value=5) )
    def minus_val(a,b,value):
        return a-value, b-value


    tasks = {
            # inputs
            'zero' : ip.Input(0),
            'one' : ip.Input(1),
            # operations
            ('ten','eleven') : (add_val, 'zero', 'one'),
            ('twenty','eleven2') : (add_val, 'ten', 'one'),
            ('fifteen', 'six') : (minus_val, 'twenty', 'eleven'),
            ('twentyfive','twentyone') : (add_val, 'fifteen','eleven2'),
            ('negativefour', 'negativefive') : (minus_val, 'one', 'zero'),
            }

    ################################################################################
    # PIPELINE CONSTRUCTION FROM TASKS
    print('RAW CONSTRUCTION')
    pipeline1 = ip.Pipeline(tasks, 'Pipeline1')
    # pipeline1.draw(show=True)

    processed1 = pipeline1.process([0,0], [1,1])
    # print(processed1)

    print('types:', pipeline1.types)
    print('shapes:', pipeline1.shapes)
    print('containers:', pipeline1.containers)


    ################################################################################
    # PIPELINE2 CONSTRUCTION FROM get_tasks()
    print('CONSRUCTION FROM get_tasks()')
    static_constructor = pipeline1.get_tasks()

    pipeline2 = ip.Pipeline(static_constructor, name="Pipeline2")
    processed2 = pipeline2.process([0,0], one=[1,1])

    assert processed1 == processed2
    assert pipeline1.uuid != pipeline2.uuid

    ################################################################################
    # SAVING AND LOADING CHECK
    print("SAVING AND LOADING")
    checksum = pipeline2.save("pipeline.pype","password")
    pipeline3 = ip.Pipeline.load("pipeline.pype", "password", checksum, name="Pipeline3")

    processed3 = pipeline3.process([0,0], one=[1,1])
    assert processed1 == processed3
    assert pipeline2.uuid != pipeline3.uuid

    # test bad checksum
    try:
        bad_pipeline = ip.Pipeline.load('pipeline.pype','password', 'not_checksum')
    except ip.PipelineError:
        pass


    ################################################################################
    # COPY CHECK
    print('SHALLOW COPY')
    pipeline4 = pipeline3.copy("Pipeline4")
    assert pipeline3.uuid != pipeline4.uuid

    # check to make sure all blocks are identical
    assert pipeline4.blocks == pipeline4.blocks.intersection(pipeline3.blocks)

    ################################################################################
    # DEEP COPY CHECK
    print('DEEP COPY')
    _ = pipeline4.deepcopy()
    pipeline5 = pipeline4.deepcopy("Pipeline5")
    assert pipeline4.uuid != pipeline5.uuid

    # check to make sure all blocks are different
    assert len( pipeline5.blocks.intersection(pipeline4.blocks) ) == 0


    ################################################################################
    # GET VIS
    pipeline5.get_vis()

    ################################################################################
    # pickle debug
    pipeline5.debug_pickle()

    ################################################################################
    # vars
    pipeline5.variables




def test_preds_and_succs():
    import imagepypelines as ip
    # some sample blocks
    @ip.blockify()
    def block1(a, b, c):
        return 'd','e','f'

    @ip.blockify()
    def block2(d, e, f, g):
        return 'h', 'i'


    tasks = {'a':ip.Input(0),
                'b':ip.Input(1),
                'c':ip.Input(2),
                ('d','e','f') : (block1,'a','b','c'),
                ('h','i') : (block2,'d','e','f','a'), # g is a
                ('final1','final2') : (block2,'a','b','c','d')
                }

    pipeline = ip.Pipeline(tasks)

    ############################################################################
    # PREDS
    d_preds = {'a', 'b', 'c'}
    final1_preds = {'a','b','c','d'}
    final2_preds = final1_preds

    assert d_preds == pipeline.get_predecessors('d')
    assert final1_preds == pipeline.get_predecessors('final1')
    assert final2_preds == pipeline.get_predecessors('final2')

    ############################################################################
    # SUCCS
    d_succs = {'h','i','final1','final2'}
    final1_succs = set()
    final2_succs = final1_succs
    a_succs = {'d','e','f','h','i','final1','final2'}

    assert d_succs == pipeline.get_successors('d')
    assert final1_succs == pipeline.get_successors('final1')
    assert final2_succs == pipeline.get_successors('final2')
    assert a_succs == pipeline.get_successors('a')



def test_Pipeline_error_checking():
    import imagepypelines as ip

    # test rejection of non-strings as variables
    try:
        not_a_string = 50
        non_string_var_tasks = { not_a_string : ip.Input() }
        ip.Pipeline(non_string_var_tasks)
    except TypeError:
        pass

    # test multiple outputs per input rejection
    try:
        multi_out_tasks = { ('out1','out2') : ip.Input() }
        ip.Pipeline(multi_out_tasks)
    except ip.PipelineError:
        pass

    # test duplicate variable rejection
    try:
        duplicate_out_tasks = { ('out','out') : ip.Input() }
        ip.Pipeline(duplicate_out_tasks)
    except ValueError:
        pass

    # test illegal variable names
    try:
        illegal_vars = {'fetches' : ip.Input(0),
                            'skip_enforcement':ip.Input(1)}
        ip.Pipeline(illegal_vars)
    except ip.PipelineError:
        pass



def test_shape_checking():
    # make sample blocks
    import imagepypelines as ip
    # some sample blocks
    @ip.blockify()
    def block1(a, b, c):
        return 'd','e','f'

    block2 = block1.deepcopy()

    block1.enforce('a', np.ndarray, [(None, 200)], tuple)
    block2.enforce('a', np.ndarray, [(200, None)], tuple)


    tasks = {'a':ip.Input(),
                'b':ip.Input(),
                'c':ip.Input(),
                ('d1','e1','f1') : (block1,'a','b','c'),
                ('d2','e2','f2') : (block2,'a','b','c'),
                }

    pipeline = ip.Pipeline(tasks)

    d = np.zeros((200,200))
    pipeline.process([d],[d],[d])

    pipeline.get_shapes_for('a')


def test_Data():
    import imagepypelines as ip

    d = ip.Data([1,2,3,4,5])

    assert d.n_batches_with('all') == 1
    assert d.n_batches_with('each') == 5

    d.pop()


    # give it bad data
    bad_data = 50

    try:
        d2 = ip.Data(bad_data)
    except TypeError:
        pass

        


# def test_Block():



class TestUtil(object):
    def test_timer_decs(self):
        import imagepypelines as ip
        import time

        @ip.timer
        def sleep1():
            time.sleep(0.01)


        @ip.timer_ms
        def sleep2():
            time.sleep(0.02)

        sleep1()
        sleep2()

    def test_Timer(self):
        import imagepypelines as ip
        import time

        t = ip.Timer()
        time.sleep(0.01)
        t.time_ms()
        t.time()

        lap1 = t.lap_ms()
        time.sleep(0.02)
        lap2 = t.lap_ms()
        assert lap2 > lap1

        t.countdown # before it's set
        t.countdown = 0.1
        while t.countdown:
            print(t.countdown)
            time.sleep(0.005)

        t.start
        str(t)


        # test bad countdown
        t2 = ip.Timer()
        try:
            t2.countdown = "not a number"
        except TypeError:
            pass




    def test_summary(self):
        import imagepypelines as ip
        import numpy as np

        test_arr = np.arange(10)

        summ = ip.arrsummary(test_arr)


        summ.summarize()
        str(summ)


        # test bad array
        try:
            ip.arrsummary("not array")
        except TypeError:
            pass



class Test_io_tools(object):
    def test_make_numbered_prefix(self):
        import imagepypelines as ip

        assert "00025" == ip.make_numbered_prefix(25)
        assert "-00100" == ip.make_numbered_prefix(-100)
        assert "-000100" == ip.make_numbered_prefix(-100,6)
        assert "-100" == ip.make_numbered_prefix(-100,2)


    def test_passgen(self):
        import imagepypelines as ip
        assert isinstance(ip.passgen("password","salt"), bytes)


    def test_prevent_overwrite(self):
        import imagepypelines as ip
        import os

        # test file and directory creation
        test_dir = 'test/test'
        test_f = 'test.txt'

        ip.prevent_overwrite(test_dir, True)
        ip.prevent_overwrite(test_f, True)

        assert ip.prevent_overwrite(test_f) == "test(1).txt"
        assert ip.prevent_overwrite(test_dir) == "test/test(1)"


        for i in range(9):
            ip.prevent_overwrite(test_f, True)

        assert ip.prevent_overwrite(test_f) == "test(10).txt"

        files_created = ["test(%s).txt" % i for i in range(1,10)] + [test_f]

        for f in files_created:
            os.remove(f)

        os.rmdir(test_dir)
        os.rmdir('test/')









#
# ################################################################################
# #                                 Image Testing
# ################################################################################
# def test_pipeline_in_pipeline():
#     import imagepypelines as ip
#     tasks = {
#             'geckos':ip.Input(0),
#             # normalize the inputs
#             'float_geckos':(ip.image.CastTo(np.float64), 'geckos'),
#             'normalized_geckos': (ip.image.NormAB(0,255), 'float_geckos'),
#             'display_safe' : (ip.image.DisplaySafe(), 'normalized_geckos'),
#             # split into RGB channels
#             ('red','green','blue') : (ip.image.ChannelSplit(), 'display_safe'),
#             # recombine into BGR and display
#             'BRswap' : (ip.image.RGBMerger(), 'blue','green','red'),
#             'numberedBRswap' : (ip.image.NumberImage(), 'BRswap'),
#             'null_data1': (ip.image.SequenceViewer(pause_for=1000), 'numberedBRswap'),
#             # 'null_data2': (ip.image.SequenceViewer(pause_for=1000), 'display_safe'),
#             }
#
#     geckoviewtest = ip.Pipeline(tasks, name='LennaViewTest')
#     geckoviewtest.process([ip.image.gecko()] * 10)
#
#
#
#
#     ################################################################################
#     # Pipeline within Pipeline
#     # this should fix the BR swap from the previous pipeline
#     tasks = {
#             'images':ip.Input(0),
#             'numberedBRswap': (geckoviewtest.asblock('numberedBRswap'), 'images'),
#             ('blue','green','red') : (ip.image.ChannelSplit(), 'numberedBRswap'),
#             'RGB' : (ip.image.RGBMerger(), 'red','green','blue'),
#             'null1' : (ip.image.SequenceViewer(pause_for=1000), 'RGB'),
#             }
#
#     pipeline_in_pipeline = ip.Pipeline(tasks, name='pipeline_in_pipeline')
#     pipeline_in_pipeline.process([ip.image.redhat(), ip.image.pig(), ip.image.carlenna()])


# import pdb; pdb.set_trace()

# TODO:
# =======
# 1 - visualization!
# 1 - DOCUMENT
# 2 - pipeline in pipeline
# 2 - arg checking
# 2 - fetches
# 3 - something something web magic?
# 3 - making the website pretty
# 4 - track statistics? extra runtime metadata? _pipeline_process kwarg
# builtin blocks!
