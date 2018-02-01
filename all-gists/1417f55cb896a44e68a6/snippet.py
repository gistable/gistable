# -*- coding: utf8 -*-

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Line
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.clock import Clock

import serial

# Basic class Float Layout
class Test1(FloatLayout):

    def __init__(self, **kwargs):
        super(Test1, self).__init__(**kwargs)

        # Set the timer for redrawing the screen
        refresh_time = 0.5
        Clock.schedule_interval(self.timer, refresh_time)

        with self.canvas:
             self.centered_circle = Line(circle = (self.center_x, self.center_y, 50), width = 2)

    def timer(self, dt):
        # Get data from serial port
        value = arduino.readline()

        # Draw the circle according to the data
        self.centered_circle.circle = (self.center_x, self.center_y,value)

        # More about drawing in Kivy here: http://kivy.org/docs/api-kivy.graphics.html


# Main App class
class SerialDataApp(App):
    def build(self):
        return Test1()

# Main program
if __name__ == '__main__':
    # Connect to serial port first
    try:
        arduino = serial.Serial('/dev/tty.usbmodem1421', 9600)
    except:
        print "Failed to connect"
        exit()

    # Launch the app
    SerialDataApp().run()

    # Close serial communication
    arduino.close()
