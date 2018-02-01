# allow less secure apps to access your Gmail at: https://support.google.com/accounts/answer/6010255?hl=en
# guide for setting up PiCamera at: https://www.raspberrypi.org/learning/getting-started-with-picamera/worksheet/
# guide for connecting PIR sensor to Pi at: https://www.raspberrypi.org/learning/parent-detector/worksheet/
# requires your email password to run (line 56), obviously a security hazard so be careful.

from gpiozero import MotionSensor
from picamera import PiCamera
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
import email.encoders
import smtplib
import os
import email
import sys
import time

camera = PiCamera()
pir = MotionSensor(4)
camera.rotation = 180 # delete or adjust to 90, 180, or 270 accordingly
h264_video = ".h264" 
mp4_video = ".mp4" 

while True:

    # record h264 video then save as mp4
    pir.wait_for_motion()
    video_name = datetime.now().strftime("%m-%d-%Y_%H.%M.%S")
    camera.start_recording(video_name + h264_video)
    pir.wait_for_no_motion()
    camera.stop_recording()
    os.system("MP4Box -add " + video_name + h264_video + " " + video_name + mp4_video) # tutorial for install to make this conversion possible at: http://raspi.tv/2013/another-way-to-convert-raspberry-pi-camera-h264-output-to-mp4
    os.system("rm " + video_name + h264_video) # delete h264 file
    footage = video_name + mp4_video

    # prepare the email
    f_time = datetime.now().strftime("%A %B %d %Y @ %H:%M:%S")
    msg = MIMEMultipart()
    msg["Subject"] = f_time
    msg["From"] = "your_address@gmail.com"
    msg["To"] = "to_address@gmail.com"
    text = MIMEText("WARNING! Motion Detected!")
    msg.attach(text)

    # attach mp4 video to email
    part = MIMEBase("application", "octet-stream")
    part.set_payload(open(footage, "rb").read())
    email.encoders.encode_base64(part)
    part.add_header("Content-Disposition", "attachment; filename= %s" % os.path.basename(footage))
    msg.attach(part)

    # access Gmail account and send email
    server = smtplib.SMTP("smtp.gmail.com:587")
    server.starttls()
    server.login("your_gmail_login","your_gmail_password")
    server.sendmail("your_address@gmail.com", "to_address@gmail.com", msg.as_string())
    server.quit()

    # delete mp4 from Pi after it has been emailed
    os.system("rm " + footage)