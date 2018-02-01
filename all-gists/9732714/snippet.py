from random import choice

def genCode(len):
  return ''.join([choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for i in range(len)])

print '%s-%s-%s-%s' % (genCode(3), genCode(3), genCode(3), genCode(3))
