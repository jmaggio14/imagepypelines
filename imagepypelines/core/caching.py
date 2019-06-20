# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018-2019 Jeff Maggio, Nathan Dileas, Ryan Hartzell
#
import os
from uuid import uuid4
import glob
import pickle
import shutil
import sys

from .. import CACHE
from .Printer import debug as ipdebug, info as ipinfo
from .Pipeline import Pipeline
from .BaseBlock import BaseBlock

ILLEGAL_CHARS = ['NUL',r'\',''//',':','*','"','<','>','|']

class Cache(object):
    """
    Object designed to store data on local storage for the purposes of object
    persistence between imagepypelines sessions or memory management.

    Args:
        None

    Attributes:
        subdir(str): the full path to the cache directory

    Example:
        >>> # let's save Lenna to our cache
        >>> import imagepypelines as ip
        >>> ip.cache['lenna'] = ip.lenna()
        >>> # retrieve lenna from cache
        >>> lenna = ip.cache['lenna']

        >>> import imagepypelines as ip
        >>> # delete everything in the cache
        >>> ip.cache.purge()

        >>> import imagepypelines as ip
        >>>
    """
    def __init__(self):
            self.subdir = os.path.join(CACHE,'cache')
            if not os.path.exists(self.subdir):
                ipinfo("creating imagepypelines cache: ", self.subdir,'...')
                os.makedirs(self.subdir)


    def filename(self, key):
        """retrieves the full filename for the specified key on the local
        machine

        Args:
            key(str): key used to cache the object

        Returns:
            str: full filename to the cached object
        """
        # ERROR CHECKING
        if not isinstance(key,str):
            raise TypeError("cache key must be a sting")

        if any( (ic in key) for ic in ILLEGAL_CHARS):
            return ValueError(
                "cache keys cannot contain illegal characters %s" % ILLEGAL_CHARS)

        # code begins here
        return os.path.join(self.subdir, key)


    def list_filenames(self):
        """list the sorted full filenames of all data in the cache"""
        return sorted( glob.glob( os.path.join(self.subdir,'*') ) )

    def list_keys(self):
        """list the cache keys of all data in the cache"""
        return sorted( os.listdir( self.subdir ) )

    def purge(self):
        """delete all items in the cache"""
        ipinfo("purging the cache...")
        for fname in self.list_filenames():
            self.remove(fname)

    def remove(self, key):
        """deletes the key specified data from the cache"""
        fname = self.filename(key)

        if os.isfile(fname):
            os.remove(fname)

        elif os.isdir(fname):
            shutil.rmtree(fname, ignore_errors=True)

    def save(self, key, obj, protocol=pickle.HIGHEST_PROTOCOL):
        """saves 'obj' to a file within the Caches directory

        Args:
            key(str): key index reference for the value to be saved,
                this will also be the name of the file in the cache directory
            obj(object): the python object to save
            protocol(int): the pickle protocol used to save the data,
                it is pickle.HIGHEST_PROTOCOL for compatability with large
                objects. You may try pickle.DEFAULT_PROTOCOL for better
                compatability

        Return:
            fname(str): the file path where the object has been cached
        """
        fname = self.filename(key)
        ipdebug("saving {} to {}".format(obj, fname))
        with open(fname,'wb') as f:
            pickle.dump(obj, f, protocol=protocol)

        return fname

    def load(self, key):
        """retrieves the key specified value from the cache

        Args:
            key(str): the key reference index for the value to be retrieved

        Returns:
            object: the unpickled cache object
        """
        ipdebug("loading {} from the cache".format(key))
        try:
            with open( self.filename(key), 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError:
            pass

        raise KeyError("no cache item with key %s" % key)


    def __getitem__(self, key):
        return self.load(key)

    def __setitem__(self, key, obj):
        self.save(key, obj)

    def __delitem__(self, key):
        self.remove(key)

    def __contains__(self,key):
        if key in self.list_keys():
            return True
        else:
            return False

    def __iter__(self):
        return (key for key in self.list_keys())

    def __len__(self,key):
        return len( self.list_keys() )

    def __str__(self):
        return "Cache at {} (contains {} items)".format(self.subdir,
                                                        len(self.list_keys()))

    def __repr__(self):
        return str(self)
