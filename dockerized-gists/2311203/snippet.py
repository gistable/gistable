#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       zipdb.py
#       Use a zipfile store a dict like k-v database.
#       Known bug: duplicate key(filenames) allowed
#       
#       Copyright 2012 mayli <mayli.he@gmail.com>
#       

import zipfile

class ZipDB(object):
    #dbfile=None
    def __init__(self,filename='tmp.zipdb',flags='a',compression=True,allowZip64=True):
        self.dbfile=zipfile.ZipFile(filename,
                flags,compression=[zipfile.ZIP_STORED,zipfile.ZIP_DEFLATED][compression],
                allowZip64=allowZip64)
    def __setitem__(self, key, item):
        """
        Method to put items into the database file.
        """
        return self.dbfile.writestr(key,item)
        
    def __getitem__(self, key):
        """
        Method to get items from the databasde file using its key
        """
        return self.dbfile.read(key)

    def __len__(self):
        """
        Returns the row count of the database file
        """
        return len(self.dbfile.namelist())

    def close(self):
        """
        Closes the database file
        """
        self.dbfile.close()

    def keys(self):
        """
        Returns a list of keys in the database file
        """
        return self.dbfile.namelist()
def main():
    def benchmark(db):
        import time
        s='.'*4*1024
        count=100000
        t1=time.time()
        for i in xrange(count):
            db[str(i)]=s
        print count/(time.time()-t1),'Insertion per second'
        t1=time.time()
        for i in xrange(count):
            tmp=db[str(i)]
        print count/(time.time()-t1),'Reads per second'
    # Usage
    d=ZipDB()
    
    # Benchmark
    benchmark(d)#compressed 8880/14862/20MB on my laptop
    d.close()
    
    d=ZipDB('tmp_uncompress.zipdb',compression=False)
    benchmark(d) #uncompressed 13802/18565/398MB on my laptop
    d.close()
    
    return 0

if __name__ == '__main__':
    main()
