============
Hello World!
============

At it's core ImagePypelines is just a way to string functions and algorithms
together.


.. doctest:: hello_world1

    >>> import imagepypelines as ip
    >>>
    >>> @ip.blockify()
    >>> def print_msg(msg):
    ...     print(msg)
    >>>
    >>> tasks = {'null':print_msg}
    >>> pipeline = ip.Pipeline(tasks)
    >>>
    >>> pipeline.process(["Hello World!"])
    Hello World!

We can pass in any data we want! In this example, we call this function
once for every datum passed in

.. doctest:: hello_world1

    >>> pipeline.process(['we','can','print','anything','individually!'])
    we
    can
    print
    anything
    individually!

Or with a simple modification we, can print everything at once! Just use the
`batch_type` parameter

.. doctest:: hello_world1

    >>> @ip.blockify(batch_type="all")
    >>> def print_all(msg):
    ...     print(msg)
    >>>
    >>> tasks = {'null':print_msg}
    >>> pipeline = ip.Pipeline(tasks)
    >>>
    >>> pipeline.process(['we','can','print','everything','at','once!'])
    ['we', 'can', 'print', 'everything', 'at', 'once!']
