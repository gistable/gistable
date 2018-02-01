#!/usr/bin/python
import random
from struct import pack
from struct import unpack
from scipy import linalg


def Str2matrix(s):
	#convert string to 4x4 matrix
	return [map(lambda x : ord(x), list(s[i:i+4])) for i in xrange(0, len(s), 4)]

def Matrix2str(m):
	#convert matrix to string
	return ''.join(map(lambda x : ''.join(map(lambda y : pack('!H', y), x)), m))

def mMatrix2str(m):
	return ''.join(map(lambda x : ''.join(map(lambda y : pack('!B', y), x)), m))

def Generate(password):
	#generate key matrix
	random.seed(password)
	return [[random.randint(0,64) for i in xrange(4)] for j in xrange(4)]

def Multiply(A,B):
	#multiply two 4x4 matrix
	C = [[0 for i in xrange(4)] for j in xrange(4)]
	for i in xrange(4):
		for j in xrange(4):
			for k in xrange(4):
				C[i][j] += (A[i][k] * B[k][j])
	return C

def Encrypt(fname):
	#encrypt file
	key = Generate('')
	data = open(fname, 'rb').read()
	length = pack('!I', len(data))
	while len(data) % 16 != 0:
		data += '\x00'
	out = open(fname + '.out', 'wb')
	out.write(length)
	for i in xrange(0, len(data), 16):
		print Str2matrix(data[i:i+16])
		cipher = Multiply(Str2matrix(data[i:i+16]), key)
		out.write(Matrix2str(cipher))
	out.close()

Encrypt('sample.wmv')

