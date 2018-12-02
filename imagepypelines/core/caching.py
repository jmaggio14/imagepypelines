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
import sys

from .. import CACHE
from .Printer import info as ipinfo
from .Pipeline import Pipeline, restore_from_pickle
from .BaseBlock import BaseBlock


def make_cache(cache_name,description=""):
    """make a new cache and add it to the imagepypelines namespace"""
    new_doc = Cache.__doc__.format(doc=description,name=cache_name)
    # create a new cache class using metaclassing
    # we use metaclassing so we can update the docstring easily
    NewCache = type(cache_name,(Cache,),{'__doc__':new_doc})
    imagepypelines_module = sys.modules['imagepypelines']
    setattr(imagepypelines_module, cache_name, NewCache(cache_name))


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
    def __init__(self,cache_name):
            self.subdir = os.path.join(CACHE,cache_name)
            if not os.path.exists(self.subdir):
                os.makedirs(self.subdir)
                ipinfo("creating Cache for: ",self.subdir)
            else:
                ipinfo("found Cache for: ",self.subdir)


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
            base,ext = os.path.splitext(basename)
            basename = "{}-{}{}".format(base, uuid4().hex[:8], ext)

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

    def restore(self,fname):
        """restores the object saved to 'fname'

        Args:
            fname(str): full file path to the object to restore

        Returns:
            obj(object): the restored (unpickled) object
        """
        fname = self.filename(fname)
        with open(fname,'rb') as f:
            raw = f.read()
        obj = pickle.loads(raw)

        if isinstance(obj,BaseBlock):
            obj.prep_for_serialization()
            return obj

        elif isinstance(obj,Pipeline):
            return restore_from_pickle(obj)

        return obj

    def __str__(self):
        return "Cache at {} (contains {} items)".format(self.subdir,
                                                        len(self.listcache()))

    def __repr__(self):
        return str(self)
