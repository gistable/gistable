import sys
import ctypes
pyint_p = ctypes.POINTER(ctypes.c_byte*sys.getsizeof(5))
five = ctypes.cast(id(5), pyint_p)
print(2 + 2 == 5) # False
five.contents[five.contents[:].index(5)] = 4
print(2 + 2 == 5) # True (must be sufficiently large values of 2 there...)