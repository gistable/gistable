import mimetypes
import sys
from collections import OrderedDict

filename = sys.argv[1]

def file_type(filename):
    type = mimetypes.guess_type(filename)
    return type

filetype = file_type(filename)[1]
if filetype == "gzip":
    import gzip
    readfile = gzip.GzipFile(filename, 'r')
else:
    readfile = open(filename,'r')

with readfile as f:
    header = next(f).strip().split("\t")
    lines = [dict(zip(header,next(f).strip().split("\t"))) for x in xrange(50000)]

schema = OrderedDict(zip(header, [bool]*len(header)))
def boolify(s):
    if s == 'True' or s == "TRUE" or s == "T":
        return True
    if s == 'False' or s == "FALSE" or s == "F":
        return False
    raise ValueError("huh?")

def autoconvert(s):
    for fn in (boolify, int, float):
        try:
            return fn(s)
        except ValueError:
            pass
    return s

type_precedence = {str:0, float:1, int:2,bool:3}
type_map = {str:"STRING", float:"FLOAT", int:"INTEGER", bool:"BOOLEAN"}

# Sense header
for line in lines:
    for k,v in line.items():
        if v == "" or v == ".":
            pass
        else:
            sense_type = type(autoconvert(v))
            if schema[k] == sense_type or schema[k] == str:
                pass
            elif type_precedence[schema[k]] > type_precedence[sense_type]:
                schema[k] = sense_type

print ','.join([ k.replace("/","_") + ":" + type_map[v] for k,v in schema.items()])

