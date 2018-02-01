
import time
import numpy as NP
from redis import StrictRedis as redis

# a 2D array to serialize
A = 10 * NP.random.randn(10000).reshape(1000, 10)

# flatten the 2D NumPy array and save it as a binary string
array_dtype = str(A.dtype)
l, w = A.shape
A = A.ravel().tostring()

# create a key as a UNIX timestamp w/ array shape appended to end of key delimited by '|'
db = redis(db=0)
key = '{0}|{1}#{2}#{3}'.format(int(time.time()), array_dtype, l, w)

# store the binary string in redis
db.set(key, A)

# retrieve the proto-array from redis
A1 = db.get(key)

# deserialize it 
array_dtype, l, w = key.split('|')[1].split('#')

A = NP.fromstring(A1, dtype=array_dtype).reshape(int(l), int(w))
