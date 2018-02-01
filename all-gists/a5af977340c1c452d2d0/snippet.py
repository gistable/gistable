#! /usr/bin/python
# Copyright (c) 2016 Rethink Robotics, Inc.

# rospy for the subscriber
import rospy
# ROS Image message
from sensor_msgs.msg import Image

def image_callback(msg, pub):
    pub.publish(msg)

def main():
    rospy.init_node('image_republisher')
    # Define your image topic
    stream_image_topic = "/cameras/left_hand_camera/image"
    # Define the Display topic
    xdisplay_topic = "/robot/xdisplay"
    # Set up your subscriber and define its callback
    pub = rospy.Publisher(xdisplay_topic, Image, queue_size=10)
    rospy.Subscriber(stream_image_topic, Image, image_callback, callback_args=pub)
    # Spin until ctrl + c
    rospy.spin()

if __name__ == '__main__':
    main()
