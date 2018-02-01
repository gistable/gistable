#!/usr/env/python

print("Converts a string to the {QUOTE} Field code")
st = raw_input("String to convert: ")
v = map(lambda y: "%s"%ord(y),st)
print("{ QUOTE %s }"%' '.join(v))