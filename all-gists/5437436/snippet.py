#Libraries to run program
import os,sys
from PIL import Image
import math
import serial as Serial
import time
import pygame
import pygame.camera

serial = Serial.Serial('/dev/ttyACM0',9600)


'''This function as for what object is to be scanned and creates a 
directory on the desktop'''
def createDir():	
	title = raw_input("Object to be scanned: ")
	desktop = r'/home/Desktop'
	direc = os.path.join(desktop,title)
	os.makedirs(direc)
	print 'Directory created on desktop!'
	return direc,title
	
'''Next it is required for the camera to capture a photo of the object 
and communicate with the arduino to continually capture and rotate 1 
step. The total number of steps for this motor is 200 steps. A '1' will
be sent to the Arduino as the controller will interprete this serial to 
rotate 1 step'''
def capture(direc,title):
	#Used to determine USB camera and enable camera
	pygame.camera.init()
	#camlist = pygame.camera.list_cameras()
	#print camlist
	cam = pygame.camera.Camera("/dev/video0",(640,480))
	cam.start()
	
	for i in range(200):
		print ('Capturing Image %i...' % i)
		image = cam.get_image()
		print ('Saving Image %i...' % i)
		image_list = [title,'_',str(i),'.jpg']
		image_name = "".join(image_list)
		image_save = os.path.join(direc,image_name)
		pygame.image.save(image,image_save)
		time.sleep(3)
		#FROM HERE DOWN...AFTER THE IMAGE IS CAPTURED AND SAVED
		#THE ARDUINO NEEDS TO BE SIGNALLED TO ROTATE 1 STEP
		serial.write('1')
		time.sleep(3)
	
	print 'Object geometry captured!!!'
	cam.stop()


'''This is completed from a directory that all has the same image
to work no the section of code that actually analysis the photos '''
def analysis(direc):
	#This contains stepper motor steps, phases on each step, angle
	#between camera and laster and iteration. The asc file is also
	#created but needs to have the path and better name
	phases = 200
	phases_each = 2*math.pi/phases
	pheta = 20*math.pi/180
	itr = 0
	out = open('Results.asc','w')
	for file in os.listdir(direc):
		scan = Image.open(os.path.join(direc,file))
		width,height = scan.size
		fi = itr*phases_each
		print 'Analyzing photo ' + file
		for y in range(height):
			maxBrightPos = [0,0]
			maxBright = 0
			for x in range(width):
				currentPos = [x,y]
				pixelRGB = scan.getpixel((x,y))
				R,G,B = pixelRGB
				brightness = R
				if (brightness>maxBright):
					maxBright = brightness
					maxBrightPos = currentPos
			b = maxBrightPos[0]-(width/2)
			ro = b/math.sin(pheta)
			
			x_coord = ro*math.cos(fi)
			y_coord = ro*math.sin(fi)
			z_coord = y
			
			if b > 0:
				out.write(str(x_coord) + ',' + str(y_coord) + ',' + str(z_coord) + '\n')
		itr = itr+1
	out.close()
	

direc, title = createDir()
capture(direc,title)
analysis(direc)

x = raw_input('')