#!/usr/bin/python

import rtmidi, time

buttons = {
    58: 'track_left',
    59: 'track_right',
    46: 'cycle',
    60: 'marker_set',
    61: 'marker_left',
    62: 'marker_right',
    43: 'rwd',
    44: 'fwd',
    42: 'stop',
    41: 'play',
    45: 'record',
    32: 's_0',
    33: 's_1',
    34: 's_2',
    35: 's_3',
    36: 's_4',
    37: 's_5',
    38: 's_6',
    39: 's_7',
    48: 'm_0',
    49: 'm_1',
    50: 'm_2',
    51: 'm_3',
    52: 'm_4',
    53: 'm_5',
    54: 'm_6',
    55: 'm_7',
    64: 'r_0',
    65: 'r_1',
    66: 'r_2',
    67: 'r_3',
    68: 'r_4',
    69: 'r_5',
    70: 'r_6',
    71: 'r_7'
}

knobs = [16, 17, 18, 19, 20, 21, 22, 23]

sliders = [0, 1, 2, 3, 4, 5, 6, 7]

def buttonDown(button):
    print "Pushed button %s" % (button, )

def buttonUp(button):
    print "Released button %s" % (button, )

def twistedKnob(idx, value):
    print "Twisted knob %d to %d" % (idx, value)

def slidSlider(idx, value):
    print "Slid slider %d to %d" % (idx, value)

def midiCallback(message, data):
    control = message[0][1]
    value = message[0][2]
    if (buttons.has_key(control)):
        name = buttons[control]
        if (value == 127):
            return buttonDown(name)
        else:
            return buttonUp(name)
    else:
        try:
            idx = knobs.index(control)
            return twistedKnob(idx, value)
        except ValueError:
            pass
        try:
            idx = sliders.index(control)
            return slidSlider(idx, value)
        except ValueError:
            pass
        
        print "Control: %d, Value: %d" % (control, value)

midiin = rtmidi.MidiIn()
port = midiin.open_port(0)
port.set_callback(midiCallback)

while True:
    time.sleep(100)
