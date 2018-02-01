"""A little script to recover deleted recording of a mongoDB db file

There's no optimization but it work and has saved me
"""

import struct
import bson
import pymongo 

import sys


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
            if 'field_1' in result and 'field_2' in result and 'field_3' in result:
                return result
    except Exception:
        return None
    return None

def generate_chunck(data, pos=0):
    "Generator to create chunck"

    print "open at: %s" % pos
    f= open(data,'rb')
    a=f.read()
    size = len(a)

    while pos < size:
        # Progress indicator
        if pos % 1024 ==0:
            print pos
        # Determine the size of the possible bson encoded data
        bson_size  = struct.unpack("<I", a[pos:pos + 4])[0]
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
connection = pymongo.Connection('localhost', 27017)

# Connect to MongoDB in order to reinsert the data
db = connection.recover_db
collection = db.recover_collection

# argv[1] = the file to recover
# argv[2] = Where to start in the file 
for chunck in generate_chunck(sys.argv[1], int(sys.argv[2])):
    result = decode_chunck(chunck)
    if result:
        print "insert"
        collection.insert(result)  

