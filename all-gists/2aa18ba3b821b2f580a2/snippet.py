#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 15/01/15
@author: Sammy Pfeiffer

# Software License Agreement (BSD License)
#
# Copyright (c) 2016, PAL Robotics, S.L.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#  * Neither the name of Willow Garage, Inc. nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

tf_interactive_marker.py contains a commandline
node that sets up a 6DOF Interactive Marker at /posestamped_im/update
and a PoseStamped topic at /posestamped and a
TF transform broadcaster with the pose of the interactive marker.
It prints on the commandline the current commandline transform and URDF
transform as you move the interactive marker.

You can stop publishing transforms doing right click
and click on Stop Publish transform.

As the help says:
Generate an interactive marker to setup your transforms.
Usage:
./tf_interactive_marker.py from_frame to frame position (x,y,z) orientation (r,p,y) or (x,y,z,w)
./tf_interactive_marker.py <from_frame> <to_frame> x y z r p y [deg]
./tf_interactive_marker.py <from_frame> <to_frame> x y z x y z w
For example (they do all the same):
./tf_interactive_marker.py base_footprint new_frame 1.0 0.0 1.0 0.0 0.0 90.0 deg
./tf_interactive_marker.py base_footprint new_frame 1.0 0.0 1.0 0.0 0.0 1.57
./tf_interactive_marker.py base_footprint new_frame 1.0 0.0 1.0 0.0 0.7071 0.7071 0.0

The output looks like:

Static transform publisher command (with roll pitch yaw):
  rosrun tf static_transform_publisher 1.0 0.0 1.0 0.0 -0.0 1.57 base_footprint new_frame 50

Static transform publisher command (with quaternion):
  rosrun tf static_transform_publisher 1.0 0.0 1.0 0.0 0.7068 0.7074 0.0 base_footprint new_frame 50

Roslaunch line of static transform publisher (rpy):
  <node name="from_base_footprint_to_new_frame_static_tf" pkg="tf" type="static_transform_publisher" args="1.0 0.0 1.0 0.0 -0.0 1.57 base_footprint new_frame 50" />

URDF format:
  <origin xyz="1.0 0.0 1.0" rpy="0.0 -0.0 1.57" />

Example usage video: https://www.youtube.com/watch?v=C9BbFv-C9Zo

"""

# based on https://github.com/ros-visualization/visualization_tutorials/blob/indigo-devel/interactive_marker_tutorials/scripts/basic_controls.py
# and https://github.com/ros-visualization/visualization_tutorials/blob/indigo-devel/interactive_marker_tutorials/scripts/menu.py

import sys
from copy import deepcopy
import rospy
from interactive_markers.interactive_marker_server import InteractiveMarkerServer
from interactive_markers.menu_handler import MenuHandler
from visualization_msgs.msg import InteractiveMarkerControl, Marker, InteractiveMarker, \
    InteractiveMarkerFeedback, InteractiveMarkerUpdate, InteractiveMarkerPose, MenuEntry
from geometry_msgs.msg import Point, Pose, PoseStamped, Vector3, Quaternion
import tf
from tf.transformations import quaternion_from_euler, euler_from_quaternion
from math import radians


class InteractiveMarkerPoseStampedPublisher():

    def __init__(self, from_frame, to_frame, position, orientation):
        self.server = InteractiveMarkerServer("posestamped_im")
        o = orientation
        r, p, y = euler_from_quaternion([o.w, o.x, o.y, o.z])
        rospy.loginfo("Publishing transform and PoseStamped from: " +
                      from_frame + " to " + to_frame +
                      " at " + str(position.x) + " " + str(position.y) + " " + str(position.z) +
                      " and orientation " + str(o.x) + " " + str(o.y) +
                      " " + str(o.z) + " " + str(o.w) + " or rpy " +
                      str(r) + " " + str(p) + " " + str(y))
        self.menu_handler = MenuHandler()
        self.from_frame = from_frame
        self.to_frame = to_frame
        # Transform broadcaster
        self.tf_br = tf.TransformBroadcaster()

        self.pub = rospy.Publisher('/posestamped', PoseStamped, queue_size=1)
        rospy.loginfo("Publishing posestampeds at topic: " + str(self.pub.name))
        pose = Pose()
        pose.position = position
        pose.orientation = orientation
        self.last_pose = pose
        self.print_commands(pose)
        self.makeGraspIM(pose)

        self.server.applyChanges()

    def processFeedback(self, feedback):
        """
        :type feedback: InteractiveMarkerFeedback
        """
        s = "Feedback from marker '" + feedback.marker_name
        s += "' / control '" + feedback.control_name + "'"

        mp = ""
        if feedback.mouse_point_valid:
            mp = " at " + str(feedback.mouse_point.x)
            mp += ", " + str(feedback.mouse_point.y)
            mp += ", " + str(feedback.mouse_point.z)
            mp += " in frame " + feedback.header.frame_id

        if feedback.event_type == InteractiveMarkerFeedback.BUTTON_CLICK:
            rospy.logdebug(s + ": button click" + mp + ".")

        elif feedback.event_type == InteractiveMarkerFeedback.MENU_SELECT:
            rospy.logdebug(s + ": menu item " + str(feedback.menu_entry_id) + " clicked" + mp + ".")
            if feedback.menu_entry_id == 1:
                rospy.logdebug("Start publishing transform...")
                if self.tf_br is None:
                    self.tf_br = tf.TransformBroadcaster()
            elif feedback.menu_entry_id == 2:
                rospy.logdebug("Stop publishing transform...")
                self.tf_br = None

            # When clicking this event triggers!
        elif feedback.event_type == InteractiveMarkerFeedback.POSE_UPDATE:
            rospy.logdebug(s + ": pose changed")

        elif feedback.event_type == InteractiveMarkerFeedback.MOUSE_DOWN:
            rospy.logdebug(s + ": mouse down" + mp + ".")

        elif feedback.event_type == InteractiveMarkerFeedback.MOUSE_UP:
            rospy.logdebug(s + ": mouse up" + mp + ".")

        # TODO: Print here the commands
        # tf static transform
        self.print_commands(feedback.pose)


        self.last_pose = deepcopy(feedback.pose)

        self.server.applyChanges()

    def print_commands(self, pose, decimals=4):
        p = pose.position
        o = pose.orientation

        print "\n---------------------------"
        print "Static transform publisher command (with roll pitch yaw):"
        common_part = "rosrun tf static_transform_publisher "
        pos_part = str(round(p.x, decimals)) + " " + str(round(p.y, decimals)) + " "+ str(round(p.z, decimals))
        r, p, y = euler_from_quaternion([o.w, o.x, o.y, o.z])
        ori_part = str(round(r, decimals)) + " " + str(round(p, decimals)) + " " + str(round(y, decimals))
        static_tf_cmd = common_part + pos_part + " " + ori_part + " " + self.from_frame + " " + self.to_frame + " 50"
        print "  " + static_tf_cmd
        print
        print "Static transform publisher command (with quaternion):"
        ori_q = str(round(o.x, decimals)) + " " + str(round(o.y, decimals)) + " " + str(round(o.z, decimals)) + " " + str(round(o.w, decimals))
        static_tf_cmd = common_part + pos_part + " " + ori_q + " " + self.from_frame + " " + self.to_frame + " 50"
        print "  " + static_tf_cmd
        print

        print "Roslaunch line of static transform publisher (rpy):"
        node_name = "from_" + self.from_frame + "_to_" + self.to_frame + "_static_tf"
        roslaunch_part = '  <node name="' + node_name + '" pkg="tf" type="static_transform_publisher" args="' +\
                         pos_part + " " + ori_part + " " + self.from_frame + " " + self.to_frame + " 50" + '" />'
        print roslaunch_part
        print

        print "URDF format:"  # <origin xyz="0.04149 -0.01221 0.001" rpy="0 0 0" />
        print '  <origin xyz="' + pos_part + '" rpy="' + ori_part + '" />'
        print "\n---------------------------"

    def makeArrow(self, msg):
        marker = Marker()

        # An arrow that's squashed to easier view the orientation on roll
        marker.type = Marker.ARROW
        marker.scale.x = 0.15
        marker.scale.y = 0.08
        marker.scale.z = 0.03
        marker.color.r = 0.3
        marker.color.g = 0.3
        marker.color.b = 0.5
        marker.color.a = 1.0

        return marker

    def makeBoxControl(self, msg):
        control = InteractiveMarkerControl()
        control.always_visible = True
        control.markers.append(self.makeArrow(msg))
        msg.controls.append(control)
        return control

    def makeGraspIM(self, pose):
        """
        :type pose: Pose
        """
        int_marker = InteractiveMarker()
        int_marker.header.frame_id = self.from_frame
        int_marker.pose = pose
        int_marker.scale = 0.3

        int_marker.name = "6dof_eef"
        int_marker.description = "transform from " + self.from_frame + " to " + self.to_frame

        # insert a box, well, an arrow
        self.makeBoxControl(int_marker)
        int_marker.controls[0].interaction_mode = InteractiveMarkerControl.MOVE_ROTATE_3D

        control = InteractiveMarkerControl()
        control.orientation.w = 1
        control.orientation.x = 1
        control.orientation.y = 0
        control.orientation.z = 0
        control.name = "rotate_x"
        control.interaction_mode = InteractiveMarkerControl.ROTATE_AXIS
        int_marker.controls.append(control)

        control = InteractiveMarkerControl()
        control.orientation.w = 1
        control.orientation.x = 1
        control.orientation.y = 0
        control.orientation.z = 0
        control.name = "move_x"
        control.interaction_mode = InteractiveMarkerControl.MOVE_AXIS
        int_marker.controls.append(control)

        control = InteractiveMarkerControl()
        control.orientation.w = 1
        control.orientation.x = 0
        control.orientation.y = 1
        control.orientation.z = 0
        control.name = "rotate_z"
        control.interaction_mode = InteractiveMarkerControl.ROTATE_AXIS
        int_marker.controls.append(control)

        control = InteractiveMarkerControl()
        control.orientation.w = 1
        control.orientation.x = 0
        control.orientation.y = 1
        control.orientation.z = 0
        control.name = "move_z"
        control.interaction_mode = InteractiveMarkerControl.MOVE_AXIS
        int_marker.controls.append(control)

        control = InteractiveMarkerControl()
        control.orientation.w = 1
        control.orientation.x = 0
        control.orientation.y = 0
        control.orientation.z = 1
        control.name = "rotate_y"
        control.interaction_mode = InteractiveMarkerControl.ROTATE_AXIS
        int_marker.controls.append(control)

        control = InteractiveMarkerControl()
        control.orientation.w = 1
        control.orientation.x = 0
        control.orientation.y = 0
        control.orientation.z = 1
        control.name = "move_y"
        control.interaction_mode = InteractiveMarkerControl.MOVE_AXIS
        int_marker.controls.append(control)

        control = InteractiveMarkerControl()
        control.orientation.w = 1
        control.orientation.x = 0
        control.orientation.y = 0
        control.orientation.z = 1
        control.name = "move_3d"
        control.interaction_mode = InteractiveMarkerControl.MOVE_3D
        int_marker.controls.append(control)

        self.menu_handler.insert("Publish transform",
                                 callback=self.processFeedback)
        self.menu_handler.insert("Stop publishing transform",
                                 callback=self.processFeedback)

        self.server.insert(int_marker, self.processFeedback)
        self.menu_handler.apply(self.server, int_marker.name)

    def run(self):
        r = rospy.Rate(20)
        while not rospy.is_shutdown():
            if self.tf_br is not None:
                pos = self.last_pose.position
                ori = self.last_pose.orientation
                self.tf_br.sendTransform(
                                         (pos.x, pos.y, pos.z),
                                         (ori.x, ori.y, ori.z, ori.w),
                                         rospy.Time.now(),
                                         self.to_frame,
                                         self.from_frame
                                         )
            ps = PoseStamped()
            ps.pose = self.last_pose
            ps.header.frame_id = self.from_frame
            ps.header.stamp = rospy.Time.now()
            self.pub.publish(ps)
            r.sleep()


def usage():
    print "Generate an interactive marker to setup your transforms."
    print "Usage:"
    print sys.argv[0] + " from_frame to frame position (x,y,z) orientation (r,p,y) or (x,y,z,w)"
    print sys.argv[0] + " <from_frame> <to_frame> x y z r p y [deg]"
    print sys.argv[0] + " <from_frame> <to_frame> x y z x y z w"
    print "For example (they all do the same):"
    print sys.argv[0] + " base_footprint new_frame 1.0 0.0 1.0 0.0 0.0 90.0 deg"
    print sys.argv[0] + " base_footprint new_frame 1.0 0.0 1.0 0.0 0.0 1.57"
    print sys.argv[0] + " base_footprint new_frame 1.0 0.0 1.0 0.0 0.0 0.7071 0.7071"
    print "You can stop publishing transforms in the right click menu of the interactive marker."

if __name__ == "__main__":
    rospy.init_node("tf_interactive_marker", anonymous=True)
    cleaned_args = rospy.myargv(sys.argv)
    if "-h" in cleaned_args or "--help" in cleaned_args:
        usage()
        exit()
    if len(cleaned_args) not in [9, 10]:
        print "Arguments error."
        usage()
        exit()
    print len(cleaned_args)
    from_frame = cleaned_args[1]
    to_frame = cleaned_args[2]
    px, py, pz = [float(item) for item in cleaned_args[3:6]]
    position = Point(px, py, pz)
    if len(cleaned_args) == 9:
        r, p, y = [float(item) for item in cleaned_args[6:]]
        quat = quaternion_from_euler(r, p, y)
        orientation = Quaternion(quat[1], quat[2], quat[3], quat[0])
    elif cleaned_args[-1] == 'deg':
        r, p, y = [radians(float(item)) for item in cleaned_args[6:-1]]
        quat = quaternion_from_euler(r, p, y)
        orientation = Quaternion(quat[1], quat[2], quat[3], quat[0])
    else:
        x, y, z, w = [float(item) for item in cleaned_args[-4:]]
        orientation = Quaternion(x, y, z, w)

    ig = InteractiveMarkerPoseStampedPublisher(from_frame, to_frame,
                                               position, orientation)
    ig.run()
