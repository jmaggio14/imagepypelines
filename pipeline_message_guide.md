# Notes
**More messages will be added.** Such as:

    - delete messages
    - error messages

# Message Structure
07/30/2020
## Graph Message
Large message indicating the node links and Block documentation

(sent when pipeline is instantiated or graph is modified)

    type : <'graph','status','reset'>
    name : <user-defined name>
    id   : <human-readable id>
    uuid : <hex uuid>
    args : <argument names in order>
    block_docs : <dictionary of block summaries (docstrings)> <== This will inform block documentation section
    nodes : <dict of node_ids & metadata>
    edges : <dict of edge_ids & metadata>
    node-link : <note-link format of graph connections https://networkx.github.io/documentation/stable/reference/readwrite/generated/networkx.readwrite.json_graph.node_link_data.html>

## Status
Update the visualization

(sent when pipeline starts or finishes a block)

    type : <'graph','status','reset'>
    name : <user-defined name>
    id   : <human-readable id>
    uuid : <hex uuid>
    nodes : <dict of updated node metadata - node_id : node_data>
    edges : <dict of edge metadata - edge_id : edge_data>

## Reset
Reset graph visualization in the UI

(sent at beginning of every pipeline run)

    type : <'graph','status','reset'>
    name : <user-defined name>
    id   : <human-readable id>
    uuid : <hex uuid>
