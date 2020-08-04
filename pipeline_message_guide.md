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
            for every block_id:
                name : <block non-unique name>
                id   : <human readable id>
                uuid : <full hex uuid>
                args : <arguments in order>
                types : <dictionary of allowed types by argument>
                shapes : <dictionary of allowed shapes by argument>
                skip_enforcement : <whether or not enforcement is allowed for this block>
                batch_type : <batching style for this block>
                tags : <list of string tags (currently unused)>
                DOCS :
                    class : <class docstring>
                    __init__ : <init docstring>
                    process : <process docstring>
        nodes : <dict of node_ids & metadata>
            args    : names of the task inputs for this block,
            outputs : names of the task outputs produced by this block,
            name    : string name of the node for visualization purposes,
            color   : color of the node for visualization purposes,
            shape   : shape of the node for visualization purposes,
            class_name : name of the class, frequently identical to the name
            validation_time: time required to validate incoming data if applicable
            processing_time : time required to process the data using this node
            avg_time_per_datum: average processing time for each datum
            num_in : number of datums coming into this node
            n_batches : number of batches for this node
            pid : process id for this node
            status: processing status. one of: ('not started', 'processing', 'done')
            display_as: indicator for how to display this node (as an "input", "sub_pipeline", "leaf", or "block")
        edges : <dict of edge_ids & metadata>
            var_name        : name of the variable in task definition
            out_index       : output index from the source node,
            in_index        : input index for the target node,
            name            : name target block's argument at the in_index
            same_type_for_all_datums    : whether or not all datums on this edge are
            the same type and shape
            data_stored_in  : the type of the container used to house the data (list, ndarray, etc)
            n_datums        : number of items of data in this edge
            datum_type      : the type of data contained, this is only
                                guaranteed to be accurate if same_type_for_all_datums is True
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
        nodes : <dict of updated node metadata - see above>
        edges : <dict of edge metadata - see above>

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
