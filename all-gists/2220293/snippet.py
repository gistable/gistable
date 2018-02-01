#!/usr/bin/python 
import time
from SimpleCV import Color, Image, np, Camera

cam = Camera() #initialize the camera
quality = 400
minMatch = 0.3

try:
    password = Image("password.jpg")
except:
    password = None

mode = "unsaved"
saved = False
minDist = 0.25


while True:
    image = cam.getImage().scale(320, 240) # get image, scale to speed things up
    faces = image.findHaarFeatures("facetrack-training.xml") # load in trained face file
    if faces:
        if not password:
            faces.draw()
            face = faces[-1]
            password = face.crop().save("password.jpg")
            break
        else:
            faces.draw()
            face = faces[-1]
            template = face.crop()
            template.save("passwordmatch.jpg")
            keypoints = password.findKeypointMatch(template,quality,minDist,minMatch)
            if keypoints:
                print "YOU ARE THE ONE!!! CONGRATS"
                question = raw_input("WOULD YOU LIKE TO CHANGE YOUR FACE PASSWORD? Y/N").strip()
                if question == "Y":
                    image = cam.getImage().scale(320, 240)
                    faces = image.findHaarFeatures("facetrack-training.xml")
                    tryit = 1
                    while not tryit == 10 or not faces:
                        image = cam.getImage().scale(320, 240)
                        faces = image.findHaarFeatures("facetrack-training.xml")
                        tryit += 1
                    if not faces:
                        "CANNOT FIND ANY FACE, QUITING"
                        break
                    else:
                        faces.draw()
                        face = faces[-1]
                        password = face.crop().save("password.jpg")
                        face.crop().show()
                        print "SUCCESSFULLY SAVED"
                        print "QUITING"
                        time.sleep(1)
                        break
                else:
                    print "OK..."
                    break
                    
            else:
                print "YOU ARE NOT THE ONE!!!"
                print "RUN AWAY OR POLICE WILL THROW YOU BEHIND THE BARS....:P"
                break
    else:
        break
