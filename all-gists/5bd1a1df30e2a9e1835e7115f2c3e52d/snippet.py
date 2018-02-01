#!/usr/bin/python
from sys import argv
from random import random 
"""
	Simple demonstration of how key entropy and key re-use drastically
	affect the way a cipher protects information.

	Visually you should be able to easyily see two things:
		- where the key bit is turned on i.e. leaks key material
		- which cipher texts are encrypted with which keys i.e. two time padness aka "two time BADNESSSSSSS" CAN I GET A WOOP WOOP
	
	for instance: 
@Keiths-MacBook-Pro:[~] 2017-08-29 13:58:43$
>python two_timepad.py 10
		      key bit that is turned on
				  V
		[*]  469714 cf904816a3734bc4cc2f1 
		[*]  469715 a0e2611f0cb2731527457
		[*]  469716 aee03a1498d1e714f8383
		[*]  469717 bb4fec1b9e6c69a21c4c4
		[*]  469718 e977721524c8449bf9b9b
		[*]  469719 0782f818ee033a9e83d8c
		[*]  469720 cc2bd3155ada902c0541a
"""
def gen_random_bytes(length):
	return [ int(random()*999)%256 for i in range(length) ]
def encrypt(plaintext,key):
	return xor(plaintext,key)
def xor(A,B):
	result = []
	for i,a in enumerate(A):
		result.append(a ^ B[i])	
	return result
def display_bytes(string):
	return "".join([ "%02x" % (i)  for i in string]) 
if __name__ == "__main__":
	if len(argv) != 2:
		print "Usage: ./%s [block length]" % (argv[0])
		print "example: ./%s 10" % (argv[0])

	block_length = int(argv[1])
	key = [0 for i in range(block_length)] #make whole key a bunch of 0s
	key[0] = int(2**8 + 1) #turn on a couple of identiable bits
	print "[*] key %d" % (key[0]) 
	pendulum_speed = 20000
	entropy_position = 0
	for i in range(1000000):
		message = gen_random_bytes(block_length) #generate random message
		cipher = encrypt(message,key) 
		print "[*] ",i,display_bytes(cipher)	
		
		if i != 0 and i%pendulum_speed == 0: #move the "on bits" up in the key array to create a "pendulum swing" effect, which behaves more like a quantum pendulum lol but it'll do ;)
			key = [0 for i in range(block_length)]
			entropy_position = 1 + (entropy_position)
			key[entropy_position%len(key)] = int(2**8 + 1)	
