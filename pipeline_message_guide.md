## Graph Message
Large message indicating the node links and Block documentation

(sent when pipeline is instantiated or graph is modified)

    type : 'graph'
    name : <user-defined name>
    id   : <human-readable id>
    uuid : <hex uuid>
    source_type : <source>
    payload :
        args : <argument names in order>
        block_docs : <dictionary of block summaries (docstrings)> <== This will inform block documentation section
        nodes : <dict of node_ids & metadata>
        edges : <dict of edge_ids & metadata>
        node-link : <note-link format of graph connections https://networkx.github.io/documentation/stable/reference/readwrite/generated/networkx.readwrite.json_graph.node_link_data.html>

## Status
Update the visualization

(sent when pipeline starts or finishes a block)

    type : 'status'
    name : <user-defined name>
    id   : <human-readable id>
    uuid : <hex uuid>
    source_type : <source>
    payload :
        nodes : <dict of updated node metadata - node_id : node_data>
        edges : <dict of edge metadata - edge_id : edge_data>

## Reset
Reset graph visualization in the UI

(sent at beginning of every pipeline run)

    type : 'reset'
    name : <user-defined name>
    id   : <human-readable id>
    uuid : <hex uuid>
    source_type : <source>
    payload :
        <empty>


## Block Error
Pipeline encountered error while processing a block

    type : 'block_error'
    name : <user-defined name>
    id   : <human-readable id>
    uuid : <hex uuid>
    source_type : <source>
    payload :
        node_id : <node uuid>
        block_name : <name of the block>
        block_id : <human readable block id>
        block_uuid : <full hex uuid>
        error_type : <type of error- ValueError, RuntimeError, etc>
        error_msg :  <message>


## Delete
Pipeline was deleted

    type : 'delete'
    name : <user-defined name>
    id   : <human-readable id>
    uuid : <hex uuid>
    source_type : <source>
    payload :
        <empty>
