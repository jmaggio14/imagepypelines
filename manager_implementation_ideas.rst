
EXPLICIT OPT-IN 1
----------------

.. code-block:: python

    import imagepypelines as ip
    ip.connect_to_dash('dash_name', host, port)

    # build the pipeline
    pipeline = ip.Pipeline(tasks)

    # build the manager
    manager = ip.Manager(work_with_dashes=['dash_name'])
    manager.add_pipeline(pipeline)

    # pauses the script here and operates remotes
    manager.start()

EXPLICIT OPT-IN 2
----------------

.. code-block:: python

    import imagepypelines as ip
    ip.connect_to_dash('dash_name', host, port)

    # build the pipeline
    pipeline = ip.Pipeline(tasks)

    # opt for control
    pipeline.enable_remote_control('dash_name')

    # pause the context and wait for remote control
    ip.start_control_loop()

IMPLICIT OPT-IN
----------------

.. code-block:: python

    import imagepypelines as ip
    ip.connect_to_dash('dash_name', host, port)

    # build the pipeline
    # pipeline's are automatically controllable via the dashboard
    pipeline = ip.Pipeline(tasks)

    # this function would pause the context and wait for remote control
    ip.start_control_loop()
