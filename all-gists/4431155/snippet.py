from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice, MonkeyImage
device = MonkeyRunner.waitForConnection()


from javax.swing import JButton, JFrame, JPanel, ImageIcon

frame = JFrame('Android Display!',
            defaultCloseOperation = JFrame.EXIT_ON_CLOSE,
            size = (960, 540)
        )

def change_text(event):
  print 'Clicked!'


def mouseUsageClicked(event):
    x = event.getX() * 2
    y = event.getY() * 2
    print(str(x)+"-"+str(y))
    device.touch(x,y,MonkeyDevice.DOWN_AND_UP)
    paintScreenshot(pan)

def paintScreenshot(p):
    result = device.takeSnapshot()
    im = ImageIcon(result.convertToBytes())
    p.graphics.drawImage(im.getImage(), 0, 0, 960, 540, p)

pan = JPanel(mouseClicked=mouseUsageClicked) #, super__paintComponent= paintScreenshot)
frame.add(pan)
frame.visible = True
