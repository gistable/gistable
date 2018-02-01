from pymouse import PyMouse
import time

m = PyMouse()

while True:
    m.click(528, 800-196, 1)
    time.sleep(3)


