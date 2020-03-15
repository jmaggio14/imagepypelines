import imagepypelines as ip

@ip.blockify( kwargs=dict(value=10) )
def add_val(a,b,value):
    return a+value, b+value

@ip.blockify( kwargs=dict(value=5) )
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

# pipeline1 - raw construction
pipeline1 = ip.Pipeline(tasks, 'Pipeline1')
# pipeline1.draw(show=True)

processed1 = pipeline1.process([0,0], [1,1])
# print(processed1)


# pipeline2 - construction from task represenation
static_constructor = pipeline1.get_tasks()

pipeline2 = ip.Pipeline(static_constructor, name="Pipeline2")
processed2 = pipeline2.process([0,0], one=[1,1])

assert processed1 == processed2
assert pipeline1.uuid != pipeline2.uuid

# SAVING AND LOADING CHECK
checksum = pipeline2.save("pipeline.pck","password")
pipeline3 = ip.Pipeline.load("pipeline.pck", "password", checksum, name="Pipeline3")

processed3 = pipeline3.process([0,0], one=[1,1])
assert processed1 == processed3
assert pipeline2.uuid != pipeline3.uuid

# COPY CHECK
pipeline4 = pipeline3.copy("Pipeline4")
assert pipeline3.uuid != pipeline4.uuid

# check to make sure all blocks are identical
assert pipeline4.blocks == pipeline4.blocks.intersection(pipeline3.blocks)


# DEEP COPY CHECK
pipeline5 = pipeline4.deepcopy("Pipeline5")
assert pipeline4.uuid != pipeline5.uuid

# check to make sure all blocks are different
assert len( pipeline5.blocks.intersection(pipeline4.blocks) ) == 0



import pdb; pdb.set_trace()



# Ryan and Jeff Enforcement brainstorming
################################################################################
# Block
# task
# tasks
# pipeline
# args
# vars
# Inputs
# 
#
# class Block():
#
#     ...
#     @property
#     def types(self):
#
#         return self._types # internal dict {arg:types}
#
#     @types.setter
#     def types(self, arg_type_dict):
#
#         self._types.update(arg_type_dict)
#
#     ############################################################################
#     @property
#     def shapes(self):
#
#         return self._shapes # internal dict {arg:shapes}
#
#     @shapes.setter
#     def shapes(self, arg_shape_dict):
#
#         self._shapes.update(arg_shape_dict)
#
#     ############################################################################
#     def enforce(self, arg='arg1', types=(type1, type2, ...), shape=(None,None,3))  OR  enforce(self, {'arg1': ((types,...), (shape)), ...})
#
#
#     #####################################################
#     # RYAN TYPE/SHAPE/ENFORCE EXAMPLE
#     #####################################################
#
#     b = Block(...)
#
#     b.types ---> {
#                     'arg1': None,
#                     'arg2': None
#                  }
#
#     b.shapes ---> {
#                     'arg1': None,
#                     'arg2': None
#                  }
#
#
#     b.types = {'arg1': (np.ndarray, nn.Tensor)}
#
#     b.types ---> {
#                     'arg1': (np.ndarray, nn.Tensor),
#                     'arg2': None
#                  }
#
#
#
# # IN shape_fns.py
# # np.ndarray
# def numpy_shape(obj):
#     return obj.shape
# # int
# def int_shape(obj):
#     return None
# # float
# def float_shape(obj):
#     return None
# # list
# def list_shape(obj):
#     return (len(obj),)
# # tuple
# def tuple_shape(obj):
#     return (len(obj),)
# # str
# def str_shape(obj):
#     return (len(obj),)
# # dict
# def dict_shape(obj):
#     return (len(obj),)
#
# ######## For actual pre-process shape check logic ####
#  1) check the pipeline's shape func dict (default + custom)
#  2) if there:
#         do thing
#     else:
#         throw error
#
#
#     ip.DEFAULT_SHAPE_FUNCS = {np.ndarray : numpy_shape,
#                                 int : int_shape,
#                                 float : float_shape,
#                                 list : list_shape,
#                                 tuple : tuple_shape,
#                                 str : str_shape,
#                                 dict : dict_shape,
#                             }
#
#     # NOTE: figure out how to update this in the plugin system
#     # install imagepypelines_tensorflow
#     # {tf.Tensor : shape_fn}
#
#     pipeline.shape_funcs = DEFAULT_SHAPE_FUNCS.copy()
#
#     pipeline.shape_funcs[new_obj] = new_obj.shape
#
# ################################################################################
#
# class block1:
#     """
#
#
#
#     Process Args:
#         A np.array containing images
#
#     Returns:
#         A list containing processed images
#
#     """
#     # batch_size = "each" --> output container is a list
#     def process(self, one_image):
#         ...
#
#
# class Resize:
#
#
# class List2Array:
#
#
#
# [processed_image1, processed_image2]
#
# class block2:
#     # batch_size = "all"
#     def process(self, image_stack):
#         neural_network(image_stack)
#
#
#
#
#
# tasks = {
#         # inputs
#         'zero' : ip.Input(0),
#         'one' : ip.Input(1),
#         # operations
#         ('ten','eleven') : (add_val, 'zero', 'one'),
#         ('twenty','eleven2') : (add_val, 'ten', 'one'),
#         ('fifteen', 'six') : (minus_val, 'twenty', 'eleven'),
#         ('twentyfive','twentyone') : (add_val, 'fifteen','eleven2'),
#         ('negativefour', 'negativefive') : (minus_val, 'one', 'zero'),
#         ('out1','out2'): (pipeline.asblock('fetch1','fetch2'), 'var1', 'var2')
#         }
#
#
#
# np.asarray(list) --> array
# pipe_block = pipeline.asblock('fetch1','fetch2') --> block obj which runs pipeline
#
# pipe_block.pipeline --> fetches actual pipeline
#
#
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


# stuff we have now
#


# pipeline_block = Pipeline.block("name of output1","name of output2")
# pipeline.dont_delete = True
# Data.fetch(pop=not self.dont_delete)
# pipeline.process_and_fetch(outputs)


########################################################################
# TEST 2 - image processing blocks test
# img_proc_tasks =



# convert the pipeline to json and back again
# pipeline2.debug_pickle()
#
# jsonified = pipeline2.to_json()
# pipeline3 = ip.from_json()
#
# processed3 = pipeline3.process([0,0], one=[1,1])
#
# assert processed3 == processed2
#
# import pdb; pdb.set_trace()



# import imagepypelines as ip
# import networkx as nx
# import numpy as np
#
# @ip.blockify(value=10)
# def add_val(a,b,value=1):
#     return a+value, b+value
#
# @ip.blockify(value=5)
# def minus_val(a,b,value=5):
#     return a-value, b-value
#
# serial_graph = {
#             # inputs
#             'data1' : ip.Input(0),
#             'data2' : ip.Input(1),
#             'constant': ip.Constant(data),
#             'other': ip.constants.PI,
#             # operations
#             ('data3','data4') : (add_val, 'data1', 'data2'),
#             # ('data3','data4') : (add_val, 'data1', 'data2'),
#             ('data6', 'data5') : (minus_val, 'data3', 'data4'),
#             ('data7','data8') : (add_val, 'data1','data3')
#             }
#
#
# pipeline = ip.Pipeline(serial_graph, 'serial_test')
# pipeline.draw(show=True)
# import pdb; pdb.set_trace()
#
#################
# def add(self, tasks):
#     if isinstance(tasks,Pipeline):
#         tasks = tasks.get_tasks()
#
#     self._build_graph(tasks)
#
# task = {('data4'): (some_func, 'data3', 'data7')}
#
# tasks = {
#             ('data9'): (some_func, 'data3', 'data7'),
#             ('data10'): (some_func, 'data4', 'data6')
#         }
#
# tasks = some_other_pipeline.get_tasks()
#
# pipeline.add(task)
# pipeline.add(tasks)
# pipeline.add(some_other_pipeline)
# pipeline += some_other_pipeline
#
# pipeline.remove(task)
# pipeline.remove(tasks)
# pipeline.remove(some_other_pipeline)
# pipeline -= some_other_pipeline
#
#
# #################
#
# processed = pipeline.process([0,0],[1,1],data9=[2,2])
# print(processed)
#
# import pdb; pdb.set_trace()



# add1 = ip.Add("Add1", {"operand1":2, "operand2":5}, {"result":None})
# add2 = ip.Add("Add2", {"operand1":3, "operand2":3}, {"result":None})
# add3 = ip.Add("Add3", {"operand1":4, "operand2":8}, {"result":None})
# add4 = ip.Add("Add4", {"operand1":200, "operand2":1000}, {"result":None})

# g = nx.MultiDiGraph()
# g.add_edges_from([
#                 (add1, add2, {"operand1":"result"}),
#                 (add3, add4, {"operand2":"result"})
#                 ])


# p1 = ip.Pipeline()
# p1.inputs["a"] = 1
# p1.inputs["b"] = 2
# p1.inputs["c"] = 3
# p1.inputs["d"] = 4
# p1.outputs["final"] = None
#
#
# p1.connect(p1.inputs, add1, "a", "operand1")
# p1.connect(p1.inputs, add1, "b", "operand2")
# p1.connect(p1.inputs, add3, "c", "operand1")
# p1.connect(p1.inputs, add3, "d", "operand2")
#
# p1.connect(add1, add3, "result", "operand2")
# p1.connect(add3, add3, "result", "operand2")
# p1.connect(add2, p1.outputs, "result", "final")
#
# p1.draw()
# p1.process()

#
# p2 = ip.Pipeline(g)
# p2.draw()
# import pdb; pdb.set_trace()
# p2.process()
#
# p3 = ip.Pipeline()
# p3.connect(add4, p1, "result", "a")
# p3.outputs["final"] = None
# p3.connect(p1, p3.outputs, "final", "final")
# p3.process()



# serial_graph = {   # create placeholder variables for input data
#             'measure_coil' : ip.Input(0),
#             'ref_coil' : ip.Input(1),
#             # move the data into a wavelet plane
#             'meas_wavelet' : (ip.Cwt(), 'measure_coil'),
#             'ref_wavelet' : (ip.Cwt(), 'ref_coil'),
#             # filter the data to 12Khz +/- 1Hz
#             'meas_filtered_12k' : (ip.GaussianFilter(mean=12e3, sigma=1), 'meas_wavelet'),
#             'ref_filtered_12k' : (ip.GaussianFilter(mean=12e3, sigma=1), 'ref_wavelet'),
#             # calculate amplitude and phase of each coil
#             'meas_amp' : (ip.Abs(), 'meas_filtered_12k'),
#             'meas_phase' : (ip.Angle(), 'meas_filtered_12k'),
#             'ref_amp' : (ip.Abs(), 'ref_filtered_12k'),
#             # calculate phase difference between the reference and measure_coil
#             'phase_diff' : (ip.Sub2(), 'meas_phase', 'ref_phase'),
#             'orientation' : ( calculate_orientation, 'meas_amp', 'phase_difference')
#             }
#
