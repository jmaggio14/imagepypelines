import os
from uuid import uuid4
import glob
from .. import CACHE, CACHE_TMP, CACHE_META, CACHE_DATASETS
from .Printer import get_printer
import pickle

class Cache(dict):
    subdir = CACHE
    printer = get_printer(CACHE)

    def __init__(self,*args,**kwargs):
        self.hashes = {}
        self.filenames = {}
        super(Cache,self).__init__(*args,**kwargs)

    def get_filename(self,key="no-key"):
        return "{}.{}".format(key,uuid4().hex[:8])

    def __setitem__(self,key,data):
        assert isinstance(key,str), "Cache keys must be a string"
        if key in self:
            self.printer.warning(
                        "replacing {}".format(self.filenames[key]) )
            self.delete( self.filenames[key] )

        self.filenames[key] = self.get_filename(key)
        with open(self[key],'wb') as f:
            pickled_obj = pickle.dumps(data)
            self.hashes[key] = hash(pickled_obj)
            f.write(pickled_obj)

    def __getitem__(self,key):
        filename = self.filenames[key]
        self.printer.info("retrieving {}".format(filename))
        with open(filename,'rb') as f:
            pickled_obj = f.read()
            data = pickle.loads(pickled_obj)

        return data

    def __delitem__(self,key):
        self.delete(key)

    def listdir(self):
        return glob.glob( os.path.join(self.subdir,'*') )

    def remove(self,key_or_fname):
        if key_or_fname in self:
            self.printer.warning("deleting {}".format(key_or_fname))
            del self[key_or_fname]
            del self.filenames[key_or_fname]
            del self.hashes[key_or_fname]
            os.remove( self.filenames[key_or_fname] )
        else:
            self.printer.warning("deleting {}".format(key_or_fname))
            os.remove(key_or_fname)

    def purge(self):
        for fname in self.listdir():
            self.remove(fname)



# -------- functions for ~/.imagepypelines/tmp ---------------
class TMP(Cache):
    subdir = CACHE_TMP

    def __del__(self):
        self.purge()

# -------- functions for ~/.imagepypelines/metadata ---------------
class METADATA(Cache):
    subdir = CACHE_META

# -------- functions for ~/.imagepypelines/datasets ---------------
class DATASETS(Cache):
    subdir = CACHE_DATASETS



tmp = TMP()
metadata = METADATA()
datasets = DATASETS()


def purge_cache():
    tmp.purge()
    metadata.purge()
    datasets.purge()
