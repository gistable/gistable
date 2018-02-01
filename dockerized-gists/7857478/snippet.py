#!/usr/bin/python


if __name__ == '__main__':
	num = raw_input()
	num = int(num) if num else 10
	l = [1]
	print l
	for i in range(num):
		l = map(lambda x,y:x+y,[0]+l,l+[0])
		print l