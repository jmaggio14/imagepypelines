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
from .Pipeline import Pipeline, restore_from_file
from .BaseBlock import BaseBlock



class Cache(object):
    subdir = CACHE
    def filename(self,basename="no-key"):
        base,ext = os.path.split(basename)
        basename = "{}.{}.{}".format(base,
                                        uuid4().hex[:8],
                                        ext)

        fname = os.path.join(self.subdir,basename)
        path = os.path.split(fname)[0]
        if not os.path.exists(path):
            os.makedirs(path)
        return fname

    def listdir(self):
        return glob.glob( os.path.join(self.subdir,'*') )

    def purge(self):
        for fname in self.listdir():
            self.remove(fname)

    def remove(self,fname):
        if os.isfile(fname):
            os.remove(fname)

        elif os.isdir(fname):
            shutil.rmtree(fname,ignore_errors=True)

    def save(self,obj):
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
                

    def retrieve(self,fname):
        obj = pickle.loads(fname)

        if isinstance(obj,'BaseBlock'):
            obj.prep_for_serialization()
            return obj

        elif isinstance(obj,Pipeline):
            return restore_from_file(fname)

        return obj





class TMP(Cache):
    subdir = CACHE_TMP

class META(Cache):
    subdir = CACHE_META

class DATASETS(Cache):
    subdir = CACHE_DATASETS

tmp = TMP()
metadata = META()
datasets = DATASETS()
