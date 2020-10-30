.. post:: 28 Oct, 2020
   :tags: science, imagepypelines, portability
   :category: Motivation
   :author: Jeff
   :excerpt: 2
   :image: 1

A Beginners Guide to Pipelines
==============================

What is a Pipeline???

In short, its everything that happens from your raw data to your results. All scripts and algorithms can be represented as a pipeline. If your background is computer science, you may have heard this concept referred to as a "graph". ImagePypelines at it's core is just a library to construct pipelines. Let's teach by example.

y = mx + b
----------

Let's say we need to make a function to apply a linear transform. Good old `y=mx+b`

.. code-block:: python

    import imagepypelines as ip

    # let's build a linear function
    @ip.blockify()
    def y(m,x,b):
        return m*x + b

    tasks = {
            # inputs
            'm' : ip.Input(0),
            'x' : ip.Input(1),
            'b' : ip.Input(2),
            # linear transformer
            'y' : (y, 'm','x','b'),
            }
    pipeline = ip.Pipeline(tasks)
