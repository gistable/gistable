import cv2
from subprocess import call, check_output

class CameraSettings:

    def __init__(self, captureObject, device):
        self.cap = captureObject
        self.device = device

    def getFocus(self):
        return int(check_output(["v4l2-ctl", "-d", self.device, "-C", "focus_absolute"]).split(":")[-1])
    
    def getContrast(self):
        return int(cap.get(cv2.cv.CV_CAP_PROP_CONTRAST)*255)

    def getBrightness(self):
        return int(cap.get(cv2.cv.CV_CAP_PROP_BRIGHTNESS)*255)
    
    def getSaturation(self):
        return int(cap.get(cv2.cv.CV_CAP_PROP_SATURATION)*255)

    def getHue(self):
        return int(cap.get(cv2.cv.CV_CAP_PROP_HUE)*255)
 
    def getGain(self):
        return int(check_output(["v4l2-ctl", "-d", self.device, "-C", "gain"]).split(":")[-1])

    def getWhiteBalance(self):
        return int(check_output(["v4l2-ctl", "-d", device, "-C", "white_balance_temperature"]).split(":")[-1])

    def setFocus(self, arg):
        call(["v4l2-ctl", "-d", self.device, "-c", "focus_auto=0"])
        call(["v4l2-ctl", "-d", self.device, "-c", "focus_absolute="+str(arg)])

    def setContrast(self, arg):
        self.cap.set(cv2.cv.CV_CAP_PROP_CONTRAST, arg/255.0)

    def setBrightness(self, arg):
        self.cap.set(cv2.cv.CV_CAP_PROP_BRIGHTNESS, arg/255.0)

    def setSaturation(self, arg):
        self.cap.set(cv2.cv.CV_CAP_PROP_SATURATION, arg/255.0)

    def setHue(self, arg):
        self.cap.set(cv2.cv.CV_CAP_PROP_HUE, arg/255.0)

    def setGain(self, arg):
        call(["v4l2-ctl", "-d", self.device, "-c", "gain="+str(arg)])

    def setWhiteBalance(self, arg):
        call(["v4l2-ctl", "-d", self.device, "-c", "white_balance_temperature_auto=0"])
        call(["v4l2-ctl", "-d", self.device, "-c", "white_balance_temperature="+str(arg)])

    def trackbar(self, windowName, trackbarName, callback, start=128, max=255):
        cv2.namedWindow(windowName)
        cv2.createTrackbar(trackbarName, windowName, start, max, callback)

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    device = "/dev/video1"
    camSettings = CameraSettings(cap, device)

    camSettings.trackbar("window", "contrast", camSettings.setContrast, camSettings.getContrast())
    camSettings.trackbar("window", "brightness", camSettings.setBrightness, camSettings.getBrightness())
    camSettings.trackbar("window", "saturation", camSettings.setSaturation, camSettings.getSaturation())
    #camSettings.trackbar("window", "gain", camSettings.setGain, camSettings.getGain())
    #camSettings.trackbar("window", "white balance", camSettings.setWhiteBalance, camSettings.getWhiteBalance(), 6500)
    #camSettings.trackbar("window", "focus", camSettings.setFocus, camSettings.getFocus(), 250)

    x = cv2.waitKey(5)
    while (x == -1):
        x = cv2.waitKey(5)
        _,image = cap.read()
        cv2.imshow("window", image)