# Using: https://developer.apple.com/library/mac/documentation/Cocoa/Reference/ObjCRuntimeRef
# Thank you to this for inspiration: https://github.com/MacLeek/trackmac/blob/master/trackmac/cocoa.py

import objc
from ctypes import CDLL, c_void_p, byref, c_char_p
from ctypes.util import find_library
from Foundation import NSMutableArray

Security = CDLL(find_library("Security"))
AuthorizationRightGet = Security.AuthorizationRightGet
db_buffer = c_void_p()
result = AuthorizationRightGet('system.preferences', byref(db_buffer))

# Cast it back to a pyobjc dict, for easy manipulation

# Doing it the easy way with pyobjc 2.5+
pyobjc_o = objc.objc_object(c_void_p=db_buffer)
# >>> pyobjc_o.className()
# u'__NSCFDictionary'

# Doing it the hard way!
objc_runtime = CDLL(find_library('objc'))

objc_getClass = objc_runtime.objc_getClass
objc_getClass.argtypes = [c_char_p]
objc_getClass.restype  = c_void_p

objc_msgSend = objc_runtime.objc_msgSend
objc_msgSend.argtypes = [c_void_p, c_void_p, c_void_p]
objc_msgSend.restype  = c_void_p

sel_registerName = objc_runtime.sel_registerName
sel_registerName.argtypes = [c_char_p]
sel_registerName.restype  = c_void_p


def memoize(function):
    memo = {}
    def wrapper(*args):
        if args in memo:
            return memo[args]
        else:
            memo[args] = function(*args)
            return memo[args]
    return wrapper

@memoize
def C(name):
    return objc_getClass(name)

@memoize
def S(name):
    return sel_registerName(name)

def send(obj, sel, param=None):
    return objc_msgSend(obj, sel, param)

temp_array = NSMutableArray.array()
# get the raw pointer of the class object
raw_temp_array = objc.pyobjc_id(temp_array)
# Add the db_buffer pointer to the array
result = send(raw_temp_array, S(b'addObject:'), db_buffer)
# Get the object back from the other side!
ctypes_o = temp_array[0]
