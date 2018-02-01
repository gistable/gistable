# 
# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <nathan.dotz@gmail.com> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return - Nathan Dotz
# ----------------------------------------------------------------------------
# 
# This script will use pygame to turn a rockband drum kit plugged in your USB
# port into a sampler.

import pygame
from pygame.locals import *

EVENTS = []

FREQ = 44100   # same as audio CD
BITSIZE = 16  # unsigned 16 bit
CHANNELS = 2   # 1 == mono, 2 == stereo
BUFFER = 1024  # audio buffer size in no. of samples
FRAMERATE = 30 # how often to check if playback has finished

def playsound(sound):
    """Play sound through default mixer channel in blocking manner.
    
    This will load the whole sound into memory before playback
    """

    sound.play()
    return sound

def main():
    pygame.init()
    
    if pygame.joystick.get_count()>1:
        print("You didn't plug in a joystick. FORSHAME!")
        return

    try:
        pygame.mixer.init(FREQ, BITSIZE, CHANNELS, BUFFER)
    except pygame.error, exc:
        print >>sys.stderr, "Could not initialize sound system: %s" % exc
        return 1

    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    

    kick = pygame.mixer.Sound("/tmp/kick.wav")
    snare = pygame.mixer.Sound("/tmp/snare.wav")
    hh = pygame.mixer.Sound("/tmp/hh.wav")
    ohh = pygame.mixer.Sound("/tmp/ohh.wav")
    # The main game loop
    current_sound = None
    while True:
        for event in pygame.event.get():
            # print event
            if event.type == JOYBUTTONDOWN:
                if current_sound != None:
                    # current_sound.stop()
                    pass
                print "Button down: ", event.button
                if event.button == 0:
                    current_sound = playsound(snare)
                if event.button == 3:
                    current_sound = playsound(kick)
                if event.button == 2:
                    current_sound = playsound(hh)
                if event.button == 1:
                    current_sound = playsound(ohh)
            if event.type == JOYBUTTONUP:
                print "Button up: ", event.button
            if event.type == JOYHATMOTION:
                print "Hat: ", event.value

main()
