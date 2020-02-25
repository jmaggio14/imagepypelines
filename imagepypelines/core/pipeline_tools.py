# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018-2020 Jeff Maggio, Nathan Dileas, Ryan Hartzell
#
from .block_subclasses import FuncBlock
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx


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
        n_roots = len(roots)
        y_max = n_roots / 2.0
        y_min = -1 * y_max
        y_vals = np.linspace(y_max, y_min, n_roots)
        pos = { n:(0,y) for n,y in zip(roots,y_vals) }


        # BRANCHES
        depths = {}
        # iterate through nodes depth-first to and compute depth
        for i,node in enumerate(branches):
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
        for depth, nodes in depths.items():
            n_nodes = len(nodes)
            y_max = n_nodes / 2.0
            y_min = -1 * y_max
            y_vals = np.linspace(y_max, y_min, n_nodes)

            for node,y in zip(nodes, y_vals):
                pos[node] = (depth, y)

        # LEAVES - TEMPORARY
        n_leaves = len(leaves)
        max_depth = max( depths.keys() )
        x = max_depth + 1
        y_max = n_leaves / 2.0
        y_min = -1 * y_max
        y_vals = np.linspace(y_max, y_min, n_leaves)

        for leaf,y in zip(leaves,y_vals):
            pos[leaf] = (x, y)



        # draw the roots (red)
        nx.draw_networkx_nodes(pipeline.graph,
                                pos,
                                nodelist=roots,
                                node_color='red',
                                node_size=1200,
                                node_shape='p',
                                ax=ax)
        # draw the branches (orange)
        nx.draw_networkx_nodes(pipeline.graph,
                                pos,
                                nodelist=branches,
                                node_color='orange',
                                node_size=1200,
                                node_shape='s',
                                ax=ax)
        # draw the leaves (green... duh)
        nx.draw_networkx_nodes(pipeline.graph,
                                pos,
                                nodelist=leaves,
                                node_color='green',
                                node_size=1200,
                                node_shape='o',
                                ax=ax)

        # label the nodes
        labels = { n : pipeline.graph.nodes[n]['name'] for n in pipeline.graph.nodes()}

        nx.draw_networkx_labels(pipeline.graph,
                                pos,
                                labels=labels,
                                ax=ax)

        # TEMPORARY
        # draw the edges
        nx.draw_networkx_edges(pipeline.graph, pos, ax=ax)

        # draw and plot the figure if the user desires it
        if show:
            plt.ion()
            plt.draw()
            plt.show()
            plt.pause(0.01)

        return ax


################################################################################
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
