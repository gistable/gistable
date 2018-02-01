#!/usr/local/bin/python
# m0xpd
# shack.nasties 'at Gee Male dot com'
import RPi.GPIO as GPIO
# setup GPIO options...
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)


class RotaryEnc:
    'Base Class for Rotary Encoder on the RPi GPIO Pins'
    
    def __init__(self,PinA,PinB,button,Position,REmin,REmax,inc):
        
        self.PinA = PinA                                        # GPIO Pin for encoder PinA
        self.PinB = PinB                                        # GPIO Pin for encoder PinB
        self.button = button                                    # GPIO Pin for encoder push button
        self.Position = Position                                # encoder 'position'
        self.min = REmin                                        # Max value
        self.max = REmax                                        # Min value
        self.inc = inc                                          # increment        
        self.old_button = 1                                     # start value for previous button state
        self.oldPinA = 1                                        # start value for previous PinA state
        self.button_release = 0                                 # initialise outputs
        self.button_down = 0                                    # initialise outputs        
        GPIO.setup(self.PinA, GPIO.IN)                          # setup IO bits...
        GPIO.setup(self.PinB, GPIO.IN)                          #
        GPIO.setup(self.button, GPIO.IN)                        #
                                                                #
    def read(self):                                             # Function to Read encoder...
        encoderPinA=GPIO.input(self.PinA)                       # get inputs...
        encoderPinB=GPIO.input(self.PinB)                       #
        if encoderPinA and not self.oldPinA:                    # Transition on PinA?
                if not encoderPinB:                             #    Yes: is PinB High?
                        self.Position=self.Position+self.inc    #        No - so we're going clockwise
                        if self.Position > self.max:            #        limit maximum value
                                self.Position = self.max        #
                                                                #
                else:                                           #
                                                                #           
                        self.Position=self.Position-self.inc    #        Yes - so we're going anti-clockwise
                        if self.Position < self.min:            #        limit minimum value
                                self.Position = self.min        #     
        self.oldPinA=encoderPinA                                #    No: just save current PinA state for next time        
                                                                #
    def read_button(self):                                      # Function to Read encoder button...
        button=GPIO.input(self.button)                          # get input...
        if button and not self.old_button:                      # 'Upward' transition on button?
            self.button_release=1                               #      Yes - so set release output
        else:                                                   #    
            self.button_release=0                               #      No - so clear it
        if not button and self.old_button:                      # 'Downward' transition on button?
            self.button_down = 1                                #       Yes - so set 'down' button
        else:                                                   #                                                
            self.button_down = 0                                #       No - so clear it
        self.old_button=button                                  # Save current button state for next time

# -------------------------------------------------------------------------------------------------------------------
# Here's a simple example of how to use the RotaryEnc Class ...
#
# Set up Rotary Encoder...
#  format is : RotaryEnc(PinA,PinB,button,Position,REmin,REmax,inc):
Position = 1                                                    # Position is also used as a variable
RE1 = RotaryEnc(12,16,18,Position,0,10,1)                       # Instatiate the encoder                         


# Main Operating Loop...
while True:
    RE1.read()                                                  # Read the encoder    
    if Position <> RE1.Position:                                # has the position changed?
        print RE1.Position                                      # Yes: so print new value
        Position = RE1.Position                                 #      and update it                
    RE1.read_button()                                           # Read the button  
    if RE1.button_down:                                         # Has it been pressed?
        print 'Button Pressed'                                  # Yes: so print a message
    if RE1.button_release:                                      # Has it been released
        print 'Button Released'                                 # Yes: so print a message
