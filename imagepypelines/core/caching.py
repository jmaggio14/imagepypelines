# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018 Jeff Maggio, Nathan Dileas, Ryan Hartzell
#
import os
from uuid import uuid4
import glob
import pickle
import shutil

from .. import CACHE, CACHE_TMP, CACHE_META, CACHE_DATASETS
from .Printer import get_printer
from .Pipeline import Pipeline, restore_from_pickle
from .BaseBlock import BaseBlock



class Cache(object):
    """
    {doc}

    Object designed to store data on local storage for the purposes of object
    persistence between imagepypelines sessions or memory management.

    Args:
        None

    Example:
        Save and Restore a Pyton Object
        >>>
        >>> # save a pythonic object
        >>> obj = "this is an example object"
        >>> fname = {name}.save(obj)
        >>>
        >>> # restore the object
        >>> obj = {name}.restore(fname)


        Get a {name} filename and save the data yourself
        >>> import numpy as np
        >>> import cv2
        >>>
        >>> random_img = np.random.rand(512,512,3)
        >>> fname = {name}.filename('optional-prefix')
        >>> cv2.imwrite(fname, random_img)
    """
    def __new__(cls):
            cls.subdir = CACHE

    def filename(self,basename="no-key"):
        """creates or retrieves the filename for the specified on the local machine

        Args:
            basename(str): optional prefix for the unique cache filename
                that will be created. OR the basename of a file that already
                exists to retrieve the full cache path of

        Example:
            Create new cache filename
            >>> fname = ip.cache.filename("optional-prefix")

            Retrieve the full filename given just the basename
            >>> fname = ip.cache.filename(basename)
        """
        basename = os.path.basename(basename)

        if basename in (os.path.basename(f) for f in self.listcache()):
            return os.path.join(self.subdir,basename)
        else:
            base,ext = os.path.split(basename)
            basename = "{}.{}.{}".format(base,
                                            uuid4().hex[:8],
                                            ext)

            return os.path.join(self.subdir,basename)


    def listcache(self):
        """list the full filenames of all data in the cache"""
        return glob.glob( os.path.join(self.subdir,'*') )

    def purge(self):
        """delete all items in the cache"""
        for fname in self.listcache():
            self.remove(fname)

    def remove(self,fname):
        """deletes the specified file"""
        if os.isfile(fname):
            os.remove(fname)

        elif os.isdir(fname):
            shutil.rmtree(fname,ignore_errors=True)

    def save(self,obj):
        """saves 'obj' to a file within the Caches directory

        Args:
            obj(object): the python object to save

        Return:
            fname(str): the file path where the object has been cached
        """
        # if it's a block, we can run it's prep_for_serialization
        # function to ensure serialization compatability
        if isinstance(obj,BaseBlock):
            obj.prep_for_serialization()
            fname = self.filename( str(obj) + '.pck' )
            self.printer.info("saving {} to {}".format(obj,fname))
            with open(fname,'wb') as f:
                pickle.dump(obj,f)

        # if it's a pipeline, we can use the pipeline's own save
        # function
        elif isinstance(obj,Pipeline):
            fname = self.filename( str(obj) + '.pck' )
            obj.save(fname)

        # otherwise if it's a generic object, we can save it
        else:
            fname = self.filename(obj.__class__.__name__ + '.pck')
            self.printer.info("saving {} to {}".format(obj,fname))
            with open(fname,'wb') as f:
                pickle.dump(obj,f)

        return os.path.basename(fname)

    def retrieve(self,fname):
        """restores the object saved to 'fname'

        Args:
            fname(str): full file path to the object to restore

        Returns:
            obj(object): the restored (unpickled) object
        """
        fname = self.filename(fname)
        obj = pickle.loads(fname)

        if isinstance(obj,'BaseBlock'):
            obj.prep_for_serialization()
            return obj

        elif isinstance(obj,Pipeline):
            return restore_from_pickle(fname)

        return obj



class TMP(Cache):
    "" + Cache.__doc__.format(doc='Temporary Cache intended for short-term '\
                            + 'temporary use (memory management)',
                            name='tmp')
    def __init__(self):
        self.subdir = CACHE_TMP

class META(Cache):
    "" + Cache.__doc__.format(doc='Persistent Cache intended for use for data '\
                            + 'in use between imagepypelines sessions',
                            name='metadata')
    def __init__(self):
        self.subdir = CACHE_META

class DATASETS(Cache):
    "" + Cache.__doc__.format(doc='Persistent Cache intended exclusively to '\
                            + 'store datasets downloaded using a webcrawler',
                            name='datasets')
    def __init__(self):
        self.subdir = CACHE_DATASETS

tmp = TMP()
metadata = META()
datasets = DATASETS()
