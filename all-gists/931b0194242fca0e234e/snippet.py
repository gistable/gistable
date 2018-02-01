#!/usr/bin/python

from __future__ import print_function
import RPi.GPIO as GPIO
from time import sleep
from random import randint

# Boards: Raspberry Pi B+/2/3/... (After B+)
# Raspberry Pi Simon Says game
# Made with 40-pin GPIO header
# Developed on Raspberry Pi 3.
# Author: Dragon5232 (Armored-Dragon)
# License: GNU GPLv3
# This project was built with 2 breadboards:
#  - big one from adafruit, connected to
#    Adafruit Pi Cobbler+. Contains:
#     - 4 color LEDs
#     - 4 color buttons
#     - 1 yellow indicator LED
#  - Small breadboard fron CanaKit
#    Jumpered 3V3 and 5V headers from
#    big board. Contains:
#     - 1 'input end' button (black)
#     - 1 red LED (loss indicator)
#     - 1 green LED (win indicator)
# Pin numbers are flexible, and can be changed.
# Refer to later comments for more info.

leds = [17, 22, 16, 19] # Yellow, Green, Blue, Red.
btns = [25, 24, 23, 18] # Yellow, Green, Blue, Red.
ipin = 21 # yellow act. indicator led pin.
dpin = 20 # 'user sequence input done/complete/finished' btn pin.
winpin = 26 # green win led pin. ONLY used IF wlmode=2
losepin = 13 # red loss led pin. ONLY used IF wlmode=2
clrs = [] # accumulated color sequence, generated
tmpin = [] # current input array, collected
instate = True # Button seq input loop
prevbtn = -1 # Previous btn index pressed
prevgen = 0 # Previous random gen num
curgen = 0 # Current random gen num
roundn = 1 # Round number
wins = 0 # Win count
losses = 0 # Lose count
wlmode = 2 # Win/Loss indicator mode.
#            Setting for how to indicate
#            the win/loss of a round.
#             - Value=1: Classic flashing of
#                        all the 4-color LEDs.
#             - Value=2: Usage of 2 additional
#                        dedicated red/green
#                        win/loss LEDs, set by
#                        winpin and losepin.

GPIO.setmode(GPIO.BCM) # cobbler numbers are bcm
GPIO.setwarnings(False) # Silence channel-in-use warnings

for led in leds: # Init LED modes
    GPIO.setup(led, GPIO.OUT)
for btn in btns: # Init button modes
    GPIO.setup(btn, GPIO.IN)
GPIO.setup(ipin, GPIO.OUT) # Init indicator LED
GPIO.setup(dpin, GPIO.IN) # Init 'done' button
if wlmode == 2:
    GPIO.setup(winpin, GPIO.OUT)
    GPIO.setup(losepin, GPIO.OUT)

def ledwipe():
    for led in leds:
        GPIO.output(led, False)
def ledpaint():
    for led in leds:
        GPIO.output(led, True)

def genrndclr():
    # 0-3. 4 leds, 4 btns.
    global prevgen
    global curgen
    while prevgen == curgen:
        curgen = randint(0, 3)
    clrs.append(curgen)
    prevgen = curgen

def ion():
    GPIO.output(ipin, True)
def ioff():
    GPIO.output(ipin, False)

try:
    while True:
        prevbtn = -1
        ioff()
        genrndclr()
        for clr in clrs:
            ledwipe()
            GPIO.output(leds[clr], True)
            sleep(0.45)
            ledwipe()
        ion()
        tmpin = []
        instate = True
        while instate: # False (not) means it's pressed
            if not GPIO.input(dpin):
                instate = False
            if not GPIO.input(btns[0]):
                if 0 != prevbtn:
                    tmpin.append(0)
                    prevbtn = 0
            if not GPIO.input(btns[1]):
                if 1 != prevbtn:
                    tmpin.append(1)
                    prevbtn = 1
            if not GPIO.input(btns[2]):
                if 2 != prevbtn:
                    tmpin.append(2)
                    prevbtn = 2
            if not GPIO.input(btns[3]):
                if 3 != prevbtn:
                    tmpin.append(3)
                    prevbtn = 3
        ioff()
        if tmpin != clrs:
            print("Round " + str(roundn) + ": Failed!")
            losses += 1
            roundn += 1
            if wlmode == 1:
                ledpaint() # 4 flashes
                sleep(0.2)
                ledwipe()
                sleep(0.1)
                ledpaint()
                sleep(0.2)
                ledwipe()
                sleep(0.1)
                ledpaint()
                sleep(0.2)
                ledwipe()
                sleep(0.1)
                ledpaint()
                sleep(0.2)
                ledwipe()
            elif wlmode == 2:
                GPIO.output(losepin, True)
                sleep(0.3)
                GPIO.output(losepin, False)
                sleep(0.2)
                GPIO.output(losepin, True)
                sleep(0.3)
                GPIO.output(losepin, False)
                sleep(0.2)
        else:
            print("Round " + str(roundn) + ": Success!")
            wins += 1
            roundn += 1
            if wlmode == 1:
                ledpaint() # 2 flashes
                sleep(0.2)
                ledwipe()
                sleep(0.1)
                ledpaint()
                sleep(0.2)
                ledwipe()
            elif wlmode == 2:
                GPIO.output(winpin, True)
                sleep(0.3)
                GPIO.output(winpin, False)
                sleep(0.2)
                GPIO.output(winpin, True)
                sleep(0.3)
                GPIO.output(winpin, False)
                sleep(0.2)
except KeyboardInterrupt:
    print("\nThanks for playing Simon Says!")
    print("Stats: " + str(roundn) + " rounds, " + str(wins) + " wins, " + str(losses) + " losses.")
    ledwipe()
    ioff()
    exit(0)
