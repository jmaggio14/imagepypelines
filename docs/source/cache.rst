=======
Caching
=======

Saving and retrieving data to disk to the cache
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The cache must be enabled before use, either with or without a password.
`ip.cache.secure_enable`
`ip.cache.insecure_enable`

calling `ip.cache.secure_enable()` with no arguments will auto-generate
a secure random passkey.

IMPORTANT!
----------
**secure_enable is not only important to safeguard your data, but to safeguard
your app!**
The ImagePypelines cache uses the pickle library internally for serialization.
This means non-encrypted cached objects can be replaced with malicious code that
make you susceptible to man-in-the-middle attacks.

When in doubt, don't use the cache and save your data using other secure methods.

.. doctest:: python

    >>> import imagepypelines as ip
    >>> # enable imagepypelines cache with a password
    >>> ip.cache.secure_enable("don't use this password")
    [...]
    >>> # save data to the cache
    >>> ip.cache['lenna'] = ip.lenna()
    >>> # retrieve the data
    >>> lenna = ip.cache['lenna']


Save Data to the cache *without* encryption (not recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. doctest:: python

    >>> import imagepypelines as ip
    >>> # enable imagepypelines cache WITHOUT a password
    >>> ip.cache.insecure_enable()
    >>> # save data to the cache
    >>> ip.cache['lenna'] = ip.lenna()
    >>> # retrieve the data
    >>> lenna = ip.cache['lenna']


Saving one object using a unique password
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
this is still secure even though a global cache password isn't set

.. doctest:: python

    >>> import imagepypelines as ip
    >>> PASSWORD = "don't use this password"
    >>> obj = ip.giza()
    >>> # enable imagepypelines cache WITHOUT a password
    >>> ip.cache.insecure_enable()
    >>> # save data to the cache
    >>> checksum = ip.cache.save('giza', obj, PASSWORD)
    >>> # retrieve the data
    >>> lenna = ip.cache.load('giza', PASSWORD, checksum)


Deleting a file in the cache
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. doctest:: python

    >>> import imagepypelines as ip
    >>> ip.cache.secure_enable()
    [...]
    >>> ip.cache['lenna'] = ip.lenna()
    >>> # delete the data on disk
    >>> del ip.cache['lenna']


Purge the entire cache
~~~~~~~~~~~~~~~~~~~~~~
enabling the cache is not required to purge it

.. doctest:: python

    >>> import imagepypelines as ip
    >>> ip.cache.purge()


Check if the value is in the cache
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. doctest:: python

    >>> import imagepypelines as ip
    >>> value_exists = ('lenna' in ip.cache)








.. END
