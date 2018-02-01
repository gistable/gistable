#!/usr/bin/python
"""A little script to recover deleted recording of a mongoDB db file

There's no optimization but it work and has saved me
"""

import struct
import bson
import pymongo 

import sys
import mmap

def decode_chunck(chunck):
    "Try to decode a chunck"
    #if not bson.is_valid(chunck):
    #    return None
    try:
        result = bson.decode_all(chunck)[0]
        if not result:
            return None
        else:
            # if there's all the searched field, return it
            if 'uploader' in result or 'user_id' in result: # and 'field_2' in result and 'field_3' in result:
                return result
    except Exception:
        #print "exception"
        return None
    #print "no expected data"
    return None

def generate_chunck(data, pos=0):
    "Generator to create chunck"

    print "open at: %s" % pos
    f= open(data,'rb')
    #a=f.read()
    a = mmap.mmap(f.fileno(),0, prot=mmap.PROT_READ)
    #size = len(a)
    size = a.size()
    max_size = 131072

    while pos < size-4:
        # Progress indicator
        if pos % 1024 ==0:
            print pos
        # Determine the size of the possible bson encoded data
        bson_size  = struct.unpack("<I", a[pos:pos + 4])[0]
        # if its deleted, guess as to its size
        if bson_size == 4008636142:
            print "possible deleted chunk"
            scanhead = pos+8 # skip over header
            # find next item
            while scanhead < size-4 and a[scanhead:scanhead + 4] != '\x07_id':
               scanhead += 1
            print "Scanned ahead " + str(scanhead)
            # figure out correct size between here and next item
            ret = None
            bson_size = 10
            while (ret == None) and pos + bson_size < scanhead and bson_size < max_size:
                bson_size += 1
                while a[pos+bson_size] != '\x00':
                   bson_size += 1
                #print "try decode with size " + str(bson_size)
                ret = decode_chunck(struct.pack("<I",bson_size) + a[pos+4:pos+bson_size])
            if ret:
               print "Possible value with size " + str(bson_size) + ": " + repr(ret)
               yield struct.pack("<I",bson_size) + a[pos+4:pos+bson_size]
               pos += bson_size
            else:
               print "no chunk found"
               pos += 1
            continue
        # If it's more than 2KB reject it (perfect for me)
        if bson_size > 2*1024:
           # Continue tu search in the file
           pos += 1
           continue
        # If the bson is bigger than the file, reject it
        if bson_size+pos > size-1:
            pos += 1
            continue 
        # A bson should end by \x00
        # http://bsonspec.org/#/specification
        if a[pos+bson_size] != '\x00':
            pos += 1
            continue
        # Chunck it 
        chunck = a[pos:pos+bson_size]
        pos += 1
        yield chunck



# create connection
connection = pymongo.MongoClient('localhost', 27017)

# Connect to MongoDB in order to reinsert the data
db = connection.recover_db
collection = db.recover_collection

# argv[1] = the file to recover
# argv[2] = Where to start in the file 
for chunck in generate_chunck(sys.argv[1], int(sys.argv[2])):
    result = decode_chunck(chunck)
    if result:
        try:
            print "insert"
            collection.insert(result)
        except pymongo.errors.DuplicateKeyError:
            None
