import cv2

# Create object to read images from camera 0
cam = cv2.VideoCapture(1)


class imgSlice(object):

    def __init__(self):
        self.x = 0
        self.y = 0
        self.w = 1
        self.h = 1

        self.capturing = False

    def test(self, event, x, y, flags, param):
        if event == 0 and self.capturing:
            self.w = x - self.x
            self.h = y - self.y
        elif event == 1:
            self.x, self.y = x, y
            self.h, self.w = 4, 4
            self.capturing = True
        elif event == 4:
            self.w = x - self.x
            self.h = y - self.y
            self.capturing = False

ims = imgSlice()
ret, img = cam.read()
cv2.imshow("Camera2", img)
cv2.setMouseCallback("Camera2", ims.test)
while True:
    # Get image from webcam
    ret, img = cam.read()
    img = cv2.resize(img, (1200, 900))
    if ims.w > 5 and ims.h > 5:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)[ims.y:ims.y + ims.h,
                                                     ims.x:ims.x + ims.w]
        eql = cv2.equalizeHist(gray)
        # show the result

        img[ims.y:ims.y + ims.h, ims.x:ims.x + ims.w, 0] = eql
        img[ims.y:ims.y + ims.h, ims.x:ims.x + ims.w, 1] = eql
        img[ims.y:ims.y + ims.h, ims.x:ims.x + ims.w, 2] = eql

    cv2.imshow("Camera2", img)
    # Sleep infinite loop for ~10ms
    # Exit if user presses <Esc>
    if cv2.waitKey(10) == 27:
        break
