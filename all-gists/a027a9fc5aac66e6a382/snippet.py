# -*- coding: utf-8 -*-
# Author: Massimo Menichinelli
# Homepage: http://www.openp2pdesign.org
# License: MIT
#

import wx
import serial

# A new custom class that extends the wx.Frame
class MyFrame(wx.Frame):

    def __init__(self, parent, title):
        super(MyFrame, self).__init__(parent, title=title,
            size=(250, 150))

        # Attach the paint event to the frame
        self.Bind(wx.EVT_PAINT, self.OnPaint)

        # Create a timer for redrawing the frame every 100 milliseconds
        self.Timer = wx.Timer(self)
        self.Timer.Start(100)
        self.Bind(wx.EVT_TIMER, self.OnPaint)

        # Show the frame
        self.Centre()
        self.Show()

    def OnPaint(self, event=None):
        # Create the paint surface
        dc = wx.PaintDC(self)

        # Refresh the display
        self.Refresh()

        # Get data from serial port
        value = arduino.readline()

        # Draw the serial data

        # Set up colors:
        thickness = 4
        border_color = "#990000"
        fill_color = "#FF944D"
        dc.SetPen(wx.Pen(border_color, thickness))
        dc.SetBrush(wx.Brush(fill_color))

        # Draw a line
        dc.DrawLine(50, 40, 50+value, 40)

        # Draw a rectangle
        dc.DrawRectangle(50,50,value,50)


# Main program
if __name__ == '__main__':
    # Connect to serial port first
    try:
        arduino = serial.Serial('/dev/tty.usbmodem1421', 9600)
    except:
        print "Failed to connect"
        exit()

    # Create and launch the wx interface
    app = wx.App()
    MyFrame(None, 'Serial data test')
    app.MainLoop()

    # Close the serial connection
    arduino.close()
