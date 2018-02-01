from picamera import PiCamera
from io import BytesIO
import socket
import time

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

with PiCamera(resolution='VGA', framerate=5) as camera:
    time.sleep(2)

    buff = BytesIO()
    for _ in camera.capture_continuous(buff, format='mjpeg'):
        sock.sendto(buff.getvalue(), ('10.10.0.10', 7000))
        buff.seek(0)
        buff.truncate()