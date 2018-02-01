#!/usr/bin/python
import SimpleCV
import time
import simplejson as json
import sys

if __name__ == "__main__":
        captureDir = '/opt/display/applications/tldisplayclient/static'
        ofilename = '%s/webcam-original.png' % captureDir
        dfilename = '%s/webcam-detected.png' % captureDir

        matches = 0
        green = (0, 255, 0)
        sleeptime = 2

        try:
                cam = SimpleCV.Camera()
        except:
                print "Can't open webcam"
                sys.exit()

        while 1:
                tstart = time.time()

                try:
                        frame = cam.getImage()
                        frame.save(ofilename)
                except:
                        print "Can't grab frame from webcam"
                        sys.exit()

                facedetect = frame.findHaarFeatures('/usr/local/share/opencv/haarcascades/haarcascade_frontalface_alt.xml')

                # Only count if we find a face
                if facedetect:
                        # Count all the matches
                        for f in facedetect:
                                matches += 1
                       
                        # Draw boxes around matches
                        facedetect.sortColorDistance(green)[0].draw(green)
                        frame.save(dfilename)
                else:
                        # Otherwise, save the undetected image for comparison
                        frame.save(dfilename)

                faces = {"faces": matches, "taken": time.time()}

                tfinish = time.time()
                faces['elapsed'] = tfinish - tstart

                facesjson = json.dumps(faces)

                f = open("/opt/display/applications/tldisplayclient/static/faces.json", 'w')
                f.write(facesjson)
                f.close()
                matches = 0
                time.sleep(sleeptime)

        sys.exit()