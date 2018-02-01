#!/usr/bin/env python
# coding: UTF-8

'''
Setup apc mini colors without Ablton Live

----------

> brew install portmidi

requirements.txt
mido

# https://github.com/olemb/mido

----------

API mini cheetsheet
http://community.akaipro.com/akai_professional/topics/midi-information-for-apc-mini


'''

import mido
import time


def led_off(note):
    return mido.Message('note_on', note=note, velocity=0)


def led_green(note):
    return mido.Message('note_on', note=note, velocity=1)


def led_green_blink(note):
    return mido.Message('note_on', note=note, velocity=2)


def led_red(note):
    return mido.Message('note_on', note=note, velocity=3)


def led_red_blink(note):
    return mido.Message('note_on', note=note, velocity=4)


def led_yellow(note):
    return mido.Message('note_on', note=note, velocity=5)


def led_yellow_blink(note):
    return mido.Message('note_on', note=note, velocity=6)


def send(output, msg):
    output.send(msg)
    time.sleep(0.0015)  # wait 1ms


def setup_apcmini():
    output = mido.open_output('APC MINI')

    # reset all
    for note in range(0, 99):
        send(output, led_off(note))

    # set for unity
    for note in range(0, 12):
        send(output, led_green(note))
    for note in range(64, 72):  # 64-71 red only
        send(output, led_red(note))

    # set for resolume avenue
    for note in range(40, 64):
        send(output, led_yellow(note))

    # set scene change
    for note in range(82, 90):  # 82 - 90 green only
        send(output, led_green(note))


if __name__ == '__main__':
    setup_apcmini()
