import random
import os
import sys
import hashlib
import thread

leetrandomness = 1;
temppassword = ""
use = False

def leet(password):
	leetwords = "aeioutsyou"
	if random.randint(0, leetrandomness) == 0:
		password = password.replace('a', str(4))
	if random.randint(0, leetrandomness) == 0:
		password = password.replace('e', str(3))
	if random.randint(0, leetrandomness) == 0:
		password = password.replace('i', str(1))
	if random.randint(0, leetrandomness) == 0:
		password = password.replace('o', str(0))
	if random.randint(0, leetrandomness) == 0:
		password = password.replace('t', str(7))
	if random.randint(0, leetrandomness) == 0:
		password = password.replace('s', '$')
	return password

def camelCase(password):
	return password.title()

def addYear(password):
	return password + str(random.randint(90,99))

def addPhone(password):
    p=list('0000000000')
    p[0] = str(random.randint(1,9))
    for i in [1,2,6,7,8]:
        p[i] = str(random.randint(0,9))
    for i in [3,4]:
        p[i] = str(random.randint(0,8))
    if p[3]==p[4]==0:
        p[5]=str(random.randint(1,8))
    else:
        p[5]=str(random.randint(0,8))
    n = range(10)
    if p[6]==p[7]==p[8]:
        n = (i for i in n if i!=p[6])
    p[9] = str(random.choice(n))
    p = ''.join(p)

    return password + p[:3] + '-' + p[3:6] + '-' + p[6:]

def addPin(password):
	return password + str(random.randint(1111,9999))

def randomSymbol():
	symbols = "!!!!$$$@@##%&*"
	return symbols[random.randint(0,13)]

def addSymbol(password):
	return password + randomSymbol()

def repeat(password):
	return password+password

def testAll():
	password = raw_input("Please enter a password: ")
	print("\nLeet:")
	print(leet(password))

	print("\nCamelCase:")
	print(camelCase(password))

	print("\nYear:")
	print(addYear(password))

	print("\nPhone:")
	print(addPhone(password))

	print("\nPin:")
	print(addPin(password))

	print("\nSymbol:")
	print(addSymbol(password))

	print("\nRepeat:")
	print(repeat(password))

def randomMangle(password):
	method = random.randint(0,60)

	if (method < 15):
		return leet(password)
	elif (method < 25):
		return addYear(password)
	elif (method < 35):
		return addSymbol(password)
	elif (method < 40):
		return camelCase(password)
	elif (method < 43):
		return addPin(password)
	elif (method < 46):
		return repeat(password)
	else:
		return password


filename = raw_input("Please enter filename: ")

def file():
	with open(filename) as readFile:
		with open(filename + ".mangled",'a') as writeFile:
			for line in readFile:

				line = line.strip()
				print("line: " + line)
				print("method: " + str(method))
				randomMangle(line)

				print("Line-Mangled: " + line)
				print("----------------------")

				writeFile.write(line)

def mangle(password):
	#print(hashlib.sha1(randomMangle(password)).hexdigest())
	try:
		password.decode('ascii')
	except UnicodeDecodeError:
		return
	else:
		if len(password) > 16:
			print password
		else:
			print(randomMangle(password))

def lengthtest(password):
	if len(password) < 7:
		if use:
			return password+temppassword
			use = False
		else:
			temppassword = password
			use = True
	else:
		return password

def randomIgnore(password):
	if random.randint(0,99) == 0:
		mangle(password)
	return


def main(argv):
	for stdline in sys.stdin:
		password = stdline.strip().replace(" ", "")
		randomIgnore(password)

	pass




if __name__ == "__main__":
    main(sys.argv)