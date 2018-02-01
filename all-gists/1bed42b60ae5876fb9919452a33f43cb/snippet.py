import random
import os
import time
os.system("clear")
print("Input order of matrix:\n")
n = int(input())
print("Input position of bot:\n")
p = int(input())
q = int(input())
print("Input position of p:\n")
x,y = [int(input()),int(input())]
while(p!=x or y!=q):
	for i in range(0,n):
		for j in range(0,n):
			if(i==x and j==y):
				print "p",
			elif(i==p and j==q):
				print "m",
			else:
				print "_",
		print("\n")
	z = random.randrange(0,2)
	if(p==x):
		if(y>q):
			q = q+1
		elif(y<q):
			q = q-1
	elif(x<p):
		if(z==1):
			if(y>q):
				q = q+1
			elif(y<q):
				q = q-1
			else:
				p = p-1
		else:
			p = p-1
	else:
		if(z==1):
			if(y>q):
				q = q+1
			elif(y<q):
				q = q-1
			else:
				p = p+1		
		else:
			p = p+1
	time.sleep(2)
	os.system("clear")
for i in range(0,n):
		for j in range(0,n):
			if(i==x and j==y):
				print "S",
			else:
				print "_",
		print("\n")
print("S for princess saved\nm for bot\np for princess\n")
