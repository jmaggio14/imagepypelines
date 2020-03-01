# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018-2020 Jeff Maggio, Nathan Dileas, Ryan Hartzell
#
from .Pipeline import Pipeline
from .block_subclasses import FuncBlock
from ..Logger import error as iperror

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import networkx as nx
import pickle
import base64
from math import sqrt, atan2, degrees

ROOT_COLOR = 'red'
ROOT_SHAPE = 'p'
ROOT_SIZE = 1200
ROOT_OUTEDGE_COLOR = 'red'

BRANCH_COLOR = 'orange'
BRANCH_SHAPE = 's'
BRANCH_SIZE = 1200
BRANCH_OUTEDGE_COLOR = 'black'

LEAF_COLOR = 'green' # (duh)
LEAF_SHAPE = 'o'
LEAF_SIZE = 400

DATA_COLOR = LEAF_COLOR
DATA_SHAPE = LEAF_SHAPE
DATA_TEXT = 10
DATA_SIZE = LEAF_SIZE
EDGE_ARROW_STYLE = "Simple,tail_width=0.5,head_width=4,head_length=8"

################################################################################
def blockify(**kwargs):
    """decorator which converts a normal function into a un-trainable
    block which can be added to a pipeline. The function can still be used
    as normal after blockification (the __call__ method is setup such that
    unfettered access to the function is permitted)

    Example:
        >>> import imagepypelines as ip
        >>>
        >>> @ip.blockify(value=10)
        >>> def add_value(datum, value):
        ...    return datum + value
        >>>
        >>> type(add_value)
        <class 'FuncBlock'>

    Args:
        **kwargs: hardcode keyword arguments for a function, these arguments
            will not have to be used to

    """
    def _blockify(func):
        return FuncBlock(func,kwargs)
    return _blockify

################################################################################
# def to_json(pipeline, pickle_protocol=pickle.HIGHEST_PROTOCOL):
#     return pipeline.to_json(pickle_protocol)
#
# ################################################################################
# def from_json(jsonified):
#     return Pipeline.from_json(jsonified)

################################################################################
def debug_pickle(pipeline):
    return pipeline.debug_pickle()

################################################################################
def categorize_nodes(pipeline):
    # --------------------------------------------------------------
    # DETERMINE THE TYPE OF EACH NODE
    # --------------------------------------------------------------
    roots = [] # outputs only
    leaves = [] # inputs only
    branches = [] # both inputs and outputs
    isolated = [] # no inputs or outputs - currently unused

    # shorthand degree functions to clean up later code
    in_degree = lambda node: pipeline.graph.in_degree(node)
    out_degree = lambda node: pipeline.graph.out_degree(node)

    for node in pipeline.graph.nodes():
        # branches
        if in_degree(node) >= 1 and out_degree(node) >= 1:
            branches.append(node)
        # isolated
        elif in_degree(node) == 0 and out_degree(node) == 0:
            isolated.append(node)
        # roots
        elif in_degree(node) == 0 and out_degree(node) >= 1:
            roots.append(node)
        # leaves
        elif in_degree(node) >= 1 and out_degree(node) == 0:
            leaves.append(node)


    return roots, branches, leaves, isolated

########################################################################
def draw_edges(pipeline, pos, ax):
    edge_names = []
    edge_x = []
    edge_y = []
    for node_a, node_b, edge_idx in pipeline.execution_order:
        pos_a = pos[node_a]
        pos_b = pos[node_b]
        edge = pipeline.graph.edges[node_a, node_b, edge_idx]

        n_edges = pipeline.graph.number_of_edges(node_a, node_b)
        y_max = n_edges/2
        y_min = -1 * y_max
        if n_edges == 1:
            y_offsets = [0]
        else:
            y_offsets = np.linspace(y_min, y_max, n_edges) * .3

        # calculate an edge label position
        # halfway between node_a and node_b along x
        # offset along y for every node
        x = (pos_a[0] + pos_b[0]) / 2
        y = (pos_a[1] + pos_b[1]) / 2 + y_offsets[edge_idx]

        edge_x.append( x )
        edge_y.append( y )
        edge_names.append( edge['var_name'] )

        # draw the arrow
        # compute the angles required for:
        # https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.patches.ConnectionStyle.html#matplotlib.patches.ConnectionStyle.Angle3

        center, radius = define_circle(pos_a, (x,y), pos_b)
        if center is None:
            connectionstyle = "arc3, rad=.20"
        else:
            connectionstyle = "arc3, rad=0.0"
            # angle_a = degrees( atan2(y-pos_a[1], x-pos_a[0]) )
            # angle_b = 90 - degrees( atan2(y-pos_b[1], x-pos_b[0]) )
            # rad = radius - sqrt( (x-center[0])**2 + (y-center[1])**2 )
            # rad = .2
            # import pdb; pdb.set_trace()
            # connectionstyle = "arc, angleA={}, angleB={}, rad={}".format(angle_a, angle_b, rad)

        arrow = patches.FancyArrowPatch(pos_a,
                                        pos_b,
                                        connectionstyle=connectionstyle,
                                        arrowstyle=EDGE_ARROW_STYLE)
        ax.add_patch(arrow)


    # draw the filled circles that represent the edge
    ax.scatter(edge_x,
                edge_y,
                s=DATA_SIZE,
                c=DATA_COLOR,
                marker=DATA_SHAPE,
                )

    # draw the edge labels and arrows
    for x,y,var_name in zip(edge_x, edge_y, edge_names):
        ax.text(x, y, var_name)


########################################################################
def visualize(pipeline, show=True, ax=None):
        # generate a new Axes if none is provided
        if ax is None:
            fig, ax = plt.subplots()

        # analyze the category of each node
        roots, branches, leaves, isolated = categorize_nodes(pipeline)

        # --------------------------------------------------------------
        # DETERMINE THE NODE LAYOUT (position)
        # --------------------------------------------------------------

        # ROOTS
        # roots go first. at x=0 and along y
        # n_roots = len(roots)
        # y_max = n_roots / 2.0
        # y_min = -1 * y_max
        # y_vals = np.linspace(y_max, y_min, n_roots)
        # pos = { n:(0,y) for n,y in zip(roots,y_vals) }


        # BRANCHES
        depths = {}
        # iterate through nodes depth-first to and compute depth
        for i,node in enumerate(pipeline.graph.nodes()):
            # compute depth as the number of predecessor nodes
            # JM: 02/25/20 THIS DOESN'T WORK
            dfs_predecessors = list( nx.dfs_predecessors(pipeline.graph, node) )
            depth = len( dfs_predecessors ) - 1

            if depth in depths:
                depths[depth].append(node)
            else:
                depths[depth] = [node]

        # draw each branch
        # x is depth, y value is arbitrary
        pos = {}
        max_depth = max( depths.keys() )
        for depth, nodes in depths.items():
            n_nodes = len(nodes)
            y_max = n_nodes / 2.0
            y_min = -1 * y_max
            y_vals = np.linspace(y_max, y_min, n_nodes)

            for node,y in zip(nodes, y_vals):
                # this subtraction is required for a left-right layout
                pos[node] = (max_depth-depth, y)

        # LEAVES - TEMPORARY
        # n_leaves = len(leaves)
        # max_depth = max( depths.keys() )
        # x = max_depth + 1
        # y_max = n_leaves / 2.0
        # y_min = -1 * y_max
        # y_vals = np.linspace(y_max, y_min, n_leaves)
        #
        # for leaf,y in zip(leaves,y_vals):
        #     pos[leaf] = (x, y)



        # draw the roots (red)
        nx.draw_networkx_nodes(pipeline.graph,
                                pos,
                                nodelist=roots,
                                node_color=ROOT_COLOR,
                                node_size=1200,
                                node_shape=ROOT_SHAPE,
                                ax=ax)
        # draw the branches (orange)
        nx.draw_networkx_nodes(pipeline.graph,
                                pos,
                                nodelist=branches,
                                node_color=BRANCH_COLOR,
                                node_size=1200,
                                node_shape=BRANCH_SHAPE,
                                ax=ax)
        # draw the leaves (green... duh)
        nx.draw_networkx_nodes(pipeline.graph,
                                pos,
                                nodelist=leaves,
                                node_color=LEAF_COLOR,
                                node_size=1200,
                                node_shape=LEAF_SHAPE,
                                ax=ax)


        # # DRAW EDGES - TEMPORARY
        # # ROOTS (inputs)
        # root_edges = []
        # for r in roots:
        #     root_edges.extend( pipeline.graph.out_edges(r) )
        #
        # nx.draw_networkx_edges(pipeline.graph,
        #                         pos,
        #                         root_edges,
        #                         edge_color=ROOT_OUTEDGE_COLOR,
        #                         ax=ax)
        #
        # # BRANCHES / LEAVES
        # branch_edges = []
        # for b in branches:
        #     branch_edges.extend( pipeline.graph.out_edges(b) )
        #
        # nx.draw_networkx_edges(pipeline.graph,
        #                         pos,
        #                         branch_edges,
        #                         edge_color=BRANCH_OUTEDGE_COLOR,
        #                         ax=ax)

        # LABELS
        # label the nodes
        labels = { n : pipeline.graph.nodes[n]['name'] for n in pipeline.graph.nodes()}
        nx.draw_networkx_labels(pipeline.graph,
                                    pos,
                                    labels=labels,
                                    ax=ax)

        # label the edges
        # edge_labels = dict(((u, v), d) for u, v, d in pipeline.graph.edges(data=True))
        draw_edges(pipeline, pos, ax)




        # draw and plot the figure if the user desires it
        if show:
            plt.ion()
            plt.draw()
            plt.show()
            plt.pause(0.01)

        return ax


################################################################################

# def find_bezier_rad(x1, y1, x2, y2, x3, y3) :
#     """
#     This function was modifed from
#     https://www.geeksforgeeks.org/equation-of-circle-when-three-points-on-the-circle-are-given/
#     """
#     x12 = x1 - x2;
#     x13 = x1 - x3;
#
#     y12 = y1 - y2;
#     y13 = y1 - y3;
#
#     y31 = y3 - y1;
#     y21 = y2 - y1;
#
#     x31 = x3 - x1;
#     x21 = x2 - x1;
#
#     # x1^2 - x3^2
#     sx13 = pow(x1, 2) - pow(x3, 2);
#
#     # y1^2 - y3^2
#     sy13 = pow(y1, 2) - pow(y3, 2);
#
#     sx21 = pow(x2, 2) - pow(x1, 2);
#     sy21 = pow(y2, 2) - pow(y1, 2);
#
#     f = (((sx13) * (x12) + (sy13) *
#           (x12) + (sx21) * (x13) +
#           (sy21) * (x13)) // (2 *
#           ((y31) * (x12) - (y21) * (x13))));
#
#     g = (((sx13) * (y12) + (sy13) * (y12) +
#           (sx21) * (y13) + (sy21) * (y13)) //
#           (2 * ((x31) * (y12) - (x21) * (y13))));
#
#     c = (-pow(x1, 2) - pow(y1, 2) -
#          2 * g * x1 - 2 * f * y1);
#
#     # eqn of circle be x^2 + y^2 + 2*g*x + 2*f*y + c = 0
#     # where centre is (h = -g, k = -f) and
#     # radius r as r^2 = h^2 + k^2 - c
#     h = -g;
#     k = -f;
#     sqr_of_r = h * h + k * k - c;
#
#     # r is the radius
#     r = round(sqrt(sqr_of_r), 5);
#
#     center = (-g, -f)
#
#     return r, center

def define_circle(p1, p2, p3):
    """
    Returns the center and radius of the circle passing the given 3 points.
    In case the 3 points form a line, returns (None, infinity).

    this function was modifed from a kind soul on stack overflow
    https://stackoverflow.com/a/50974391
    """
    temp = p2[0] * p2[0] + p2[1] * p2[1]
    bc = (p1[0] * p1[0] + p1[1] * p1[1] - temp) / 2
    cd = (temp - p3[0] * p3[0] - p3[1] * p3[1]) / 2
    det = (p1[0] - p2[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p2[1])

    if abs(det) < 1.0e-6:
        return (None, np.inf)

    # Center of circle
    cx = (bc*(p2[1] - p3[1]) - cd*(p1[1] - p2[1])) / det
    cy = ((p1[0] - p2[0]) * cd - (p2[0] - p3[0]) * bc) / det

    radius = np.sqrt((cx - p1[0])**2 + (cy - p1[1])**2)
    return ((cx, cy), radius)


#                                CLASSES
################################################################################

# DO NOT DELETE!!! - may be useful in future
# class Data(object):
#     def __init__(self,data):
#         self.data = data
#         if isinstance(data, np.ndarray):
#             self.type = "array"
#         elif isinstance(data, (list,tuple)):
#             self.type = "iter"
#         else:
#             self.type = "iter"
#             self.data = [self.data]
#
#     def batch_data(self):
#         return self.data
#
#     def datums(self):
#         if self.type == "iter":
#             for d in self.data:
#                 yield d
#
#         elif self.type == "array":
#             # return every row of data
#             for r in range(self.data.shape[0]):
#                 yield self.data[r]
#
#     def __iter__(self):
#         return self.datums()
