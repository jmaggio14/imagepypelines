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
from cryptography.fernet import Fernet
import base64
import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


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

            self.__passwd = None
            self.__enabled = False

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
        for fname in self.list_keys():
            self.remove(fname)

    def secure_enable(self, passwd=None):
        """sets a default encryption key for all data saved to the cache,
        by default is a long random key

        Args:
            passwd(str): default password for this cache
        Returns:
            None
        """
        if passwd is None:
            passwd = uuid4().hex

        assert isinstance(passwd, str),"passwd must a string"
        self.__passwd = passwd
        self.__enabled = True
        return self.__passwd

    def insecure_enable(self):
        self.__passwd = None
        self.__enabled = True

    @staticmethod
    def passgen(passwd=None, salt=''):
        """generate a hashed key from a password, will generate something
        entirely random by default

        Args:
            passwd (None,str): optional, password to hash. a random one will be
                generated if none is provided
            salt (str): optional, salt for your password. Unused if password is
                not provided

        Returns:
            bytes: hashed passkey safe string
        """
        if passwd is None:
            passwd = uuid4().hex

        assert isinstance(passwd, str), "passwd must a string"
        assert isinstance(salt, str), "salt must be a string"
        # generate a proper key using Fernet library
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt.encode(),
            iterations=100000,
            backend=default_backend()
        )
        return base64.urlsafe_b64encode( kdf.derive(passwd.encode()) )

    def remove(self, key):
        """deletes the key specified data from the cache

        Args:
            key(str): key for the object in the cache

        Returns:
            bool: whether or not the object was successfully deleted
        """
        fname = self.filename(key)

        if os.path.isfile(fname):
            os.remove(fname)

        elif os.path.isdir(fname):
            shutil.rmtree(fname, ignore_errors=True)

        return (not os.path.exists(fname))

    def save(self, key, obj, passwd=None, protocol=pickle.HIGHEST_PROTOCOL):
        """saves 'obj' to a file within the Caches directory

        Args:
            key(str): key index reference for the value to be saved,
                this will also be the name of the file in the cache directory
            obj(object): the python object to save
            passwd(str,None): the encryption key for this object, defaults to
                the cache password set by ip.cache.passwd(). If no password
                is provided and none is set prior using ip.cache.passwd, then
                no encryption will be used.
            protocol(int): the pickle protocol used to save the data,
                it is pickle.HIGHEST_PROTOCOL for compatability with large
                objects. You may try pickle.DEFAULT_PROTOCOL for better
                compatability

        Return:
            fname(str): the file path where the object has been cached
        """
        self.__check_if_enabled()
        fname = self.filename(key)
        raw_bytes = pickle.dumps(obj, protocol=protocol)

        if passwd is None:
            # if there is no global passwd, then don't encrypt the pickled obj
            if self.__passwd is None:
                encoded = raw_bytes
            # default to the global cache password if it has been set
            else:
                fernet = Fernet( self.passgen(self.__passwd) )
                encoded = fernet.encrypt(raw_bytes)
        else:
            fernet = Fernet( self.passgen(passwd) )
            encoded = fernet.encrypt(raw_bytes)

        ipdebug("saving {} to {}".format(obj, fname))
        with open(fname,'wb') as f:
            f.write(encoded)

        return fname

    def load(self, key, passwd=None):
        """retrieves the key specified value from the cache

        Args:
            key(str): the key reference index for the value to be retrieved
            passwd(str,None): the encryption key for this object, defaults to
                the cache password set by ip.cache.passwd(). If no password
                is provided and none is set prior using ip.cache.passwd, then
                no encryption is assumed.

        Returns:
            object: the unpickled cache object
        """
        self.__check_if_enabled()
        ipdebug("loading {} from the cache...".format(key))
        fname = self.filename(key)

        # load the raw bytes from disk
        raise_keyerror = False
        try:
            with open(fname, 'rb') as f:
                raw_bytes = f.read()
        except FileNotFoundError:
            raise_keyerror = True

        # raise a key error if we can't load or otherwise find the file
        if raise_keyerror:
            raise KeyError("no cache item with key %s" % key)

        # decrypt the data if necessary
        if passwd is None:
            # if there is no global passwd, then don't decrypt the pickled obj
            if self.__passwd is None:
                decoded = raw_bytes
            # default to the global cache password if it has been set
            else:
                fernet = Fernet( self.passgen(self.__passwd) )
                decoded = fernet.decrypt(raw_bytes)

        else:
            fernet = Fernet( self.passgen(passwd) )
            decoded = fernet.decrypt(raw_bytes)

        # unpickle the object
        no_error = True
        try:
            obj = pickle.loads( decoded )
        except pickle.UnpicklingError:
            raise_cacheerror = False

        if not no_error:
            raise CachingError(
                "unable to load data from cache. Was it encrypted" \
                + " with a different password?")

        return obj

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
        return "Cache at {} (contains {} items)".format(self.subdir, len(self))

    def __repr__(self):
        return str(self)

    def enabled(self):
        return self.__enabled

    def __check_if_enabled(self):
        if self.__enabled:
            return

        raise CachingError("cache must be enabled before you can save or load "\
                    + "any objects. see ip.cache.secure_enable "\
                    + "or ip.cache.insecure_enable "\
                    + "(a password is required for secure use!)")
