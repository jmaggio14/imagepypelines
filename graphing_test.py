import imagepypelines as ip
import networkx as nx
import numpy as np

@ip.blockify(value=10)
def add_val(a,b,value):
    return a+value, b+value

@ip.blockify(value=5)
def minus_val(a,b,value):
    return a-value, b-value

serial_graph = {
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


pipeline = ip.Pipeline(serial_graph, 'serial_test')
pipeline.draw(show=True)

processed = pipeline.process([0,0],one=[1,1])
print(processed)
import pdb; pdb.set_trace()



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
#         tasks = tasks.get_static_representation()
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
# tasks = some_other_pipeline.get_static_representation()
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
