=======
Caching
=======

Caching
-------

Saving and retrieving data to disk to the cache
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. doctest:: python

    >>> import imagepypelines as ip
    >>> # save data to the cache
    >>> ip.cache['lenna'] = ip.lenna()
    >>> # retrieve the data
    >>> lenna = ip.cache['lenna']


Deleting a file in the cache
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. doctest:: python

    >>> import imagepypelines as ip
    >>> ip.cache['lenna'] = ip.lenna()
    >>> # delete the data on disk
    >>> del ip.cache['lenna']


Purge the entire cache
~~~~~~~~~~~~~~~~~~~~~~

.. doctest:: python

    >>> import imagepypelines as ip
    >>> ip.cache.purge()


Check if the value is in the cache
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. doctest:: python

    >>> import imagepypelines as ip
    >>> value_exists = ('lenna' in ip.cache)








.. END
