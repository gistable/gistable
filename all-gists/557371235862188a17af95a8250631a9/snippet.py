import time
import os

width  = 236
height = 70

sleep  = 0

word   = "Hai"

oneD   = True

def main():

	menu()

	wordLen = len(word)

	xDirection = 1
	yDirection = 1

	x = 0
	y = 0
	
	if oneD:
		offset = 0
	else:
		offset = 1

	while True:
	
		if not oneD:
			os.system('cls' if os.name == 'nt' else 'clear')
		
		print ( ("\n" * (y * offset)) + (" " * x) + word)

		x += xDirection
		y += yDirection

		if x <= 0 or x >= width - wordLen:
			xDirection *= -1

		if y <= 0 or y >= height:
			yDirection *= -1

		time.sleep(speed)
		

def menu():
	global width
	global height
	global word
	global oneD
	global speed
	
	usrIn = input("Width (enter for " + str(width) + "): ")
	
	if not usrIn == "":
		width = int(usrIn)

	usrIn = input("Height (enter for " + str(height) + "): ")

	if not usrIn == "":
		height = int(usrIn)

	usrIn = input("Word (enter for '" + word + "'): ")

	if not usrIn == "":
		word = usrIn

	usrIn = input("One dimensional or two: ")

	oneD = usrIn == "1"
	
	usrIn = input("Delay speed in seconds (enter for no delay): ")

	if not usrIn == "":
		speed = float(usrIn)
	else:
		speed = 0
		
main()
