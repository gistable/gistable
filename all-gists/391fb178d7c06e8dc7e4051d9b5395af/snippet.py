#!/usr/bin/env python

# sudo apt-get install tesseract-ocr
# sudo pip install pytesseract

# Author: Sammy Pfeiffer

try:
    import Image
except ImportError:
    from PIL import Image
import pytesseract
import rospy
from std_msgs.msg import String
from sensor_msgs.msg import CompressedImage
import cv2
import numpy as np
from actionlib import SimpleActionClient
try:
    from cerevoice_tts_msgs.msg import TtsAction, TtsGoal
except ImportError:
    print "Couldn't import TtsActionGoal, we won't speak"


class TextReader(object):
    def __init__(self):
        self.last_img = None
        self.img_sub = rospy.Subscriber('/wide_stereo/left/image_color/compressed',
                                        CompressedImage,
                                        self.img_cb)
        self.pub_text = rospy.Publisher('/recognized_text', String)
        self.speaking = False
        try:
            self.tts_ac = SimpleActionClient('/tts', TtsAction)
            rospy.loginfo("Waiting for TTS AS...")
            self.tts_ac.wait_for_server()
            rospy.loginfo("Found TTS AS!")
            self.speaking = True
        except NameError:
            pass

    def img_cb(self, data):
        self.last_img = data

    def get_text(self, image):
        np_arr = np.fromstring(image.data, np.uint8)
        image_np = cv2.imdecode(np_arr, cv2.CV_LOAD_IMAGE_COLOR)
        cv2.imwrite('/tmp/current_image_reading.png', image_np)
        text = pytesseract.image_to_string(
            Image.open('/tmp/current_image_reading.png'))
        return text

    def say_sentence(self, text):
        rospy.loginfo("I'll say:" + text)
        text = text.replace('1', 'I')
        text = text.replace('\n', '')
        g = TtsGoal()
        g.text = text
        self.tts_ac.send_goal_and_wait(g)
        rospy.sleep(1)

    def run(self):
        r = rospy.Rate(1)
        while not rospy.is_shutdown():
            if self.last_img:
                text = self.get_text(self.last_img)
                if text:
                    rospy.loginfo("I read: " + str(text))
                    self.pub_text.publish(text)
                    if self.speaking:
                        self.say_sentence(text)
                    rospy.loginfo("I couldn't read anything.")
            r.sleep()


if __name__ == '__main__':
    rospy.init_node('text_reader')
    tr = TextReader()
    tr.run()
