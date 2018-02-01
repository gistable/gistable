#!/usr/bin/python
'''
Author: Zoetrope Ltd.
MJPEG stream from DSLR with autofocus
Based on Igor Maculan's simple mjpg http server:
https://gist.github.com/n3wtron/4624820
'''
import camera
from PIL import Image, ImageFilter, ImageChops, ImageStat, ImageDraw
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import StringIO
import time

def estimateFocus(file, s=5):
    im = Image.open(file).convert("L")
    w,h = im.size
    box = (w/2 - 50, h/2 - 50, w/2 + 50, h/2 + 50)
    im = im.crop(box)
    imf = im.filter(ImageFilter.MedianFilter(s))
    d = ImageChops.subtract(im, imf, 1, 100)
    return ImageStat.Stat(d).stddev[0]

def setManualFocus(camm, focusPoint):
    focusList = ['Near 1', 'Near 2', 'Near 3', 'None', 'Far 1', 'Far 2', 'Far 3']
    conf = camera.Config(camm)
    root = conf.get_root_widget()
    child = root.get_child_by_name("manualfocusdrive")
    child.set_value(focusList[focusPoint])
    conf.set_config()


class focusStateMachine():

    def __init__(self):
        self.focusValues = []
        self.state = self.moveToEnd
        self.coarseList = []
        self.mediumList = []
        self.fineList = []
        self.returnState = None
        self.currentRelPos = [0,0,0]

    def moveToEnd(self):
        print "move to end"
        self.state = self.moveTo
        self.returnState = self.focusCoarse
        self.currentRelPos = [0,0,0]
        self.moveToParam = [0,0,-6]


    def moveTo(self):
        print "Moving: current = {}, target = {}, focus is {}".format(self.currentRelPos, self.moveToParam, estimateFocus("preview.jpg"))
        if self.currentRelPos == self.moveToParam:
            self.state = self.returnState
            print "Move finished!"
            self.currentRelPos = [0,0,0]
            return
        else:
            #Check coarse
            if self.currentRelPos[2] != self.moveToParam[2]:
                if self.currentRelPos[2] < self.moveToParam[2]:
                    setManualFocus(capture, 6)
                    self.currentRelPos[2] += 1
                else:
                    setManualFocus(capture, 2)
                    self.currentRelPos[2] -= 1
                time.sleep(0.12)
            elif self.currentRelPos[1] != self.moveToParam[1]:
                if self.currentRelPos[1] < self.moveToParam[1]:
                    setManualFocus(capture, 5)
                    self.currentRelPos[1] += 1
                else:
                    setManualFocus(capture, 1)
                    self.currentRelPos[1] -= 1
                time.sleep(0.07)
            elif self.currentRelPos[0] != self.moveToParam[0]:
                if self.currentRelPos[0] < self.moveToParam[0]:
                    setManualFocus(capture, 4)
                    self.currentRelPos[0] += 1
                else:
                    setManualFocus(capture, 0)
                    self.currentRelPos[0] -= 1
                time.sleep(0.04)

    def focusCoarse(self):
        coarseCount = len(self.coarseList)

        self.coarseList.append(estimateFocus("preview.jpg"))
        print "Coarse no. {}: currently: {}".format(coarseCount,estimateFocus("preview.jpg"))

        if (coarseCount == 7):
            index = self.coarseList.index(max(self.coarseList))
            self.moveToParam = [0,2,-(7-index)]
            self.state = self.moveTo
            self.returnState = self.focusMedium

            self.run()

            return


        self.state = self.moveTo
        self.moveToParam = [0,0,1]


    def focusMedium(self):
        currentFocus = estimateFocus("preview.jpg")

        self.mediumList.append(currentFocus)

        print "Medium {}: currently = {}".format(len(self.mediumList), currentFocus)
        if len(self.mediumList) > 2:
            if  self.mediumList[-1] < (0.95 * self.mediumList[-2]):
                ##Go back to best focus point and change state
                self.state = self.moveTo
                self.currentRelPos = [0,0,0]
                self.moveToParam = [0,2,0]
                self.returnState = self.focusFine
                return

        self.state = self.moveTo
        self.moveToParam = [0,-1,0]

        return

    def focusFine(self):
        currentFocus = estimateFocus("preview.jpg")
        print "Fine {}: currently = {}".format(len(self.fineList), currentFocus)

        self.fineList.append(currentFocus)

        if (len(self.fineList) > 2):
            if self.fineList[-1] < (0.99 * self.fineList[-2]):
                self.state = self.moveTo
                self.moveToParam = [1,0,0]
                self.returnState = self.done
                print "Done"
                return

        self.state = self.moveTo
        self.moveToParam = [-1,0,0]

    def done(self):
        pass

    def run(self):
        self.state()





class CamHandler(BaseHTTPRequestHandler):

    def grabFrameAndDisplay(self):
        frame = capture.preview_to_file("preview.jpg")
        jpg = Image.open("preview.jpg")
        w,h = jpg.size
        box = (w/2 - 50, h/2 - 50, w/2 + 50, h/2 + 50)
        draw = ImageDraw.Draw(jpg)
        draw.rectangle(box, outline='red')
        tmpFile = StringIO.StringIO()
        jpg.save(tmpFile,'JPEG')
        self.wfile.write("--jpgboundary")
        self.send_header('Content-type','image/jpeg')
        self.send_header('Content-length',str(tmpFile.len))
        self.end_headers()
        jpg.save(self.wfile,'JPEG')


    def do_GET(self):
        if self.path.endswith('.mjpg'):
            self.send_response(200)
            self.send_header('Content-type','multipart/x-mixed-replace; boundary=--jpgboundary')
            self.end_headers()
            focus = focusStateMachine()
            while True:
                try:
                    self.grabFrameAndDisplay()
                    focus.run()

                except KeyboardInterrupt:
                    break
            return
        if self.path.endswith('.html'):
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write('<html><head></head><body>')
            self.wfile.write('<img src="cam.mjpg"/>')
            self.wfile.write('</body></html>')
            return

def main():
    global capture
    capture = camera.Camera()
    try:
        server = HTTPServer(('',8084),CamHandler)
        print "server started"
        server.serve_forever()
    except KeyboardInterrupt:
        server.socket.close()

if __name__ == '__main__':
    main()
