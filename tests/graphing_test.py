import numpy as np



def testcore():
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
    checksum = pipeline2.save("pipeline.pck","password")
    pipeline3 = ip.Pipeline.load("pipeline.pck", "password", checksum, name="Pipeline3")

    processed3 = pipeline3.process([0,0], one=[1,1])
    assert processed1 == processed3
    assert pipeline2.uuid != pipeline3.uuid

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
    pipeline5 = pipeline4.deepcopy("Pipeline5")
    assert pipeline4.uuid != pipeline5.uuid

    # check to make sure all blocks are different
    assert len( pipeline5.blocks.intersection(pipeline4.blocks) ) == 0



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
