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
from cryptography.fernet import Fernet, InvalidToken
import base64
import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.exceptions import InvalidSignature
import hashlib


from .. import CACHE
from .. import debug as ipdebug, info as ipinfo
from .Pipeline import Pipeline
from .BaseBlock import BaseBlock
from .Exceptions import CachingError, ChecksumError


ILLEGAL_CHARS = ['NUL',
                '\\',
                '/',
                ':',
                '*',
                '"',
                '<',
                '>',
                '|']
"""illegal characters for cache keys to ensure that they don't raise OS errors"""

class Cache(object):
    """
    Object designed to store data on local storage for the purposes of object
    persistence between imagepypelines sessions or memory management.

    Args:
        None

    Attributes:
        subdir(str): the full path to the cache directory

    Example:
        >>> import imagepypelines as ip
        >>> # enable imagepypelines cache with a password
        >>> ip.cache.secure_enable("don't use this password")
        >>> # save data to the cache
        >>> ip.cache['lenna'] = ip.lenna()
        >>> # retrieve the data
        >>> lenna = ip.cache['lenna']


        >>> import imagepypelines as ip
        >>> PASSWORD = "don't use this password"
        >>> obj = ip.giza()
        >>> # enable imagepypelines cache WITHOUT a password
        >>> ip.cache.insecure_enable()
        >>> # save data to the cache
        >>> checksum = ip.cache.save('giza', obj, PASSWORD)
        >>> # retrieve the data
        >>> lenna = ip.cache.load('giza', PASSWORD, checksum)
    """
    def __init__(self):
            self.subdir = os.path.join(CACHE,'cache')
            if not os.path.exists(self.subdir):
                ipinfo("creating imagepypelines cache: " + self.subdir +'...')
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

        Raises:
            TypeError: if cache key is not a string
            ValueError: if cache key contains illegal characters
        """
        # ERROR CHECKING
        if not isinstance(key,str):
            raise TypeError("cache key must be a sting")

        if any( (ic in key) for ic in ILLEGAL_CHARS):
            raise ValueError(
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
            passwd = self.random_password()

        assert isinstance(passwd, str),"passwd must a string"
        self.__passwd = passwd
        self.__enabled = True
        return self.__passwd

    def insecure_enable(self):
        self.__passwd = None
        self.__enabled = True

    @staticmethod
    def random_password():
        return uuid4().hex

    @staticmethod
    def checksum(key):
        """returns a sha256 hash of the file contents
        Args:
            key(str): key for the object in the cache

        Returns:
            str: sha256 checksum as hex string

        Raises:
            KeyError: if no associated key is found
        """
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

        return __checksum_bytes(raw_bytes)

    @staticmethod
    def __checksum_bytes(raw_bytes):
        """returns a sha256 hash of the file contents
        Args:
            raw_bytes(bytes): the file contents as a bytes objects

        Returns:
            str: sha256 checksum as hex string
        """
        return hashlib.sha256(raw_bytes).hexdigest()

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
            passwd = Cache.random_password()

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
        return base64.urlsafe_b64encode( kdf.derive( passwd.encode() ) )

    @staticmethod
    def encrypt(raw_bytes, passwd):
        """encrypts the given object using fernet symmetrical encryption

        Args:
            raw_bytes(bytes): raw bytes to encrypt into an picklable form
            passwd(str): string password as to hash into the encryption key

        Returns:
            bytes: encrypted object

        """
        fernet = Fernet( Cache.passgen(passwd) )
        encoded = fernet.encrypt(raw_bytes)
        return encoded

    @staticmethod
    def decrypt(raw_bytes, passwd):
        """decrypts the given object using fernet symmetrical encryption

        Args:
            raw_bytes(bytes): raw bytes to decrypt into an unpicklable form
            passwd(str): string password as to hash into the encryption key

        Returns:
            bytes: decrypted object

        Raises:
            CachingError: if data decryption failed
        """
        fernet = Fernet( Cache.passgen(passwd) )

        error = True
        try:
            decoded = fernet.decrypt(raw_bytes)
        except (InvalidSignature, InvalidToken):
            error = False

        if not error:
            raise CachingError(
                "unable to decrypt data. Is the password correct?")

        return decoded

    def remove(self, key):
        """deletes the key specified data from the cache

        Args:
            key(str): key for the object in the cache

        Returns:
            bool: whether or not the object was successfully deleted

        Raises:
            KeyError: if no key associated with the cache item was found
        """
        fname = self.filename(key)

        if os.path.isfile(fname):
            os.remove(fname)

        elif os.path.isdir(fname):
            shutil.rmtree(fname, ignore_errors=True)

        else:
            raise KeyError("no cache item with key %s" % key)

        return (not os.path.exists(fname))

    def save(self, key, obj, passwd=None, protocol=pickle.HIGHEST_PROTOCOL):
        """saves 'obj' to a file within the Caches directory

        Args:
            key(str): key index reference for the value to be saved,
                this will also be the name of the file in the cache directory
            obj(object): the python object to save
            passwd(str,None): the encryption key for this object, defaults to
                the cache password set by ip.cache.secure_enable().
                If no password is provided and none is set prior using
                ip.cache.secure_enable(), then no encryption will be used.
            protocol(int): the pickle protocol used to save the data,
                it is pickle.HIGHEST_PROTOCOL for compatability with large
                objects. You may try pickle.DEFAULT_PROTOCOL for better
                compatability

        Returns:
            str: sha256 checksum of the file contents

        TODO:
            automatically compress data before encryption
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
                encoded = self.encrypt(raw_bytes, self.__passwd)
        else:
            encoded = self.encrypt(raw_bytes, passwd)

        checksum = self.__checksum_bytes(encoded)

        ipdebug("saving {} to {}. checksum: {}".format(obj, fname, checksum))
        with open(fname,'wb') as f:
            f.write(encoded)

        return checksum

    def load(self, key, passwd=None, checksum=None):
        """retrieves the key specified value from the cache

        Args:
            key(str): the key reference index for the value to be retrieved
            passwd(str,None): the encryption key for this object, defaults to
                the cache password set by ip.cache.secure_enable().
                If no password is provided and none is set prior using
                ip.cache.secure_enable(), then no encryption is assumed.
            checksum(str): checksum to check file contents against before
                unpickling

        Returns:
            object: the unpickled cache object

        Raises:
            KeyError: if no key associated with the cache item was found
            CachingError: if unable to unpickle the data
            ChecksumError: if the given checksum doesn't match the checksum read
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

        # perform a checksum check on the raw bytes if a checksum is provided
        if checksum:
            assert isinstance(checksum, str),"checksum must be a hex string"
            file_checksum = self.__checksum_bytes(raw_bytes)
            if file_checksum != checksum:
                raise ChecksumError("file checksum {} doesn't match given"\
                        + " checksum {} ".format(file_checksum, checksum) )

        # decrypt the data if necessary
        if passwd is None:
            # if there is no global passwd, then don't decrypt the pickled obj
            if self.__passwd is None:
                decoded = raw_bytes
            # default to the global cache password if it has been set
            else:
                decoded = self.decrypt(raw_bytes, self.__passwd)
        else:
            decoded = self.decrypt(raw_bytes, passwd)

        # unpickle the object
        no_error = True
        try:
            obj = pickle.loads( decoded )
        except pickle.UnpicklingError:
            no_error = False

        if not no_error:
            raise CachingError("Unable to unpickle data. Is it corrupt?")

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

    def __len__(self):
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
