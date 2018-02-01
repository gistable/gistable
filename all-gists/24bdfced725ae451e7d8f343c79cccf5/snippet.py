#!/usr/bin/env python

import os
import math
from numpy import interp
from random import choice, sample
from time import sleep
from math import log1p
# from colour import Color

ROOT = "/sys/bus/hid/drivers/hid-razer/0003:1532:020F.0003"
ROW_COUNT = 6
COL_COUNT = 16

def clamp(x): 
    return max(0, min(x, 255))

def write_to_file(filename, value):
    with open(os.path.join(ROOT, filename), 'w') as outfile:
        outfile.write(value)

def set_keyboard_rgb(rgb_list):
    """
    Set all keys rgb values. Takes list of tups.
    """

    hex_str = ''.join(
        map(
            lambda tup: ''.join(map(chr, tup)),
            rgb_list
        )
    )

    write_to_file('set_key_colors', hex_str)

def solid_color(*rgb):
    rgb_list = [rgb]*ROW_COUNT*COL_COUNT
    set_keyboard_rgb(rgb_list)

def two_color_noise(rgb1,rgb2,variety=64,burst=True,secs=10,per_sec=10):
    def set_colors():
        rgb_list = sample([rgb1, rgb2]*ROW_COUNT*COL_COUNT*16, ROW_COUNT*COL_COUNT)
        for i in range(ROW_COUNT*COL_COUNT):
            r,g,b = rgb_list[i]
            r += choice(range(-variety/2, variety/2))
            g += choice(range(-variety/2, variety/2))
            b += choice(range(-variety/2, variety/2))
            rgb_list[i] = tuple(map(clamp, [r,g,b]))
        set_keyboard_rgb(rgb_list)

    if burst:
        for _ in range(secs*per_sec):
            set_colors()
            sleep(1.0/per_sec)
    else:
        set_colors()

def monochrome_noise(red,green,blue,variety=64,burst=True,secs=10,per_sec=10):
    def set_colors():
        rgb_list = [(red,green,blue)]*ROW_COUNT*COL_COUNT
        for i in range(ROW_COUNT*COL_COUNT):
            r,g,b = rgb_list[i]
            r += choice(range(-variety/2, variety/2))
            g += choice(range(-variety/2, variety/2))
            b += choice(range(-variety/2, variety/2))
            rgb_list[i] = tuple(map(clamp, [r,g,b]))
        # print rgb_list
        set_keyboard_rgb(rgb_list)

    if burst:
        for _ in range(secs*per_sec):
            set_colors()
            sleep(1.0/per_sec)
    else:
        set_colors()



def random_burst(secs=10, per_sec=10, bright=False, sparseness=0):
    for interval in range(secs*per_sec):
        if bright:
            rng = [0,255]
        else:
            rng = range(256)

        rgb_list = [
            choice([tuple([choice(rng) for x in range(3)])]+[(0,0,0)]*sparseness) for y in range(ROW_COUNT*COL_COUNT)
        ]

        # print rgb_list

        set_keyboard_rgb(rgb_list)

        sleep(1.0/per_sec)


def r_wipe(count=5, r_color=(255,0,0), bg_color=(0,255,0), twinkle=True, line=False):

    def make_random_color(dominant_ix, variety):
        init_rgb = sample(range(variety)*3, 3)
        init_rgb[dominant_ix] = choice(range(256-variety,256))
        return tuple(init_rgb)

    if line:
        starting_pt = 0
        line_variance = 64
    else:
        starting_pt = -3
        line_variance = 1

    for interval in range(count):
        for i in range(starting_pt, COL_COUNT):
            if twinkle:
                dominant_bg_ix = bg_color.index(max(bg_color))
                rgb_list = [
                    make_random_color(dominant_bg_ix, 100) for y in range(ROW_COUNT*COL_COUNT)
                ]
            else:
                rgb_list = [bg_color]*ROW_COUNT*COL_COUNT

            # if i >= 0:
            rl = [i+x for x in range(0,ROW_COUNT*COL_COUNT,16)]

            if not line:
                if -3 <= i <= -1:
                    to_add = [ rl[0]+3, rl[1]+3, rl[4]+3, rl[5]+3 ]
                elif -2 <= i <= -1:
                    to_add = [ rl[0]+2, rl[0]+3, rl[1]+3, rl[2]+2, rl[3]+2, rl[4]+2, rl[4]+3, rl[5]+3 ]
                elif -1 <= i <= 12:
                    to_add = [ rl[0]+1, rl[0]+2, rl[0]+3, rl[1]+3, rl[2]+1, rl[2]+2, rl[3]+2, rl[4]+2, rl[4]+3, rl[5]+3 ]
                elif -1 <= i <= 13:
                    to_add = [ rl[0]+1, rl[0]+2, rl[2]+1, rl[2]+2, rl[3]+2, rl[4]+2 ]
                elif -1 <= i <= 14:
                    to_add = [ rl[0]+1, rl[2]+1 ]

                if rl < 0:
                    rl = to_add
                else:
                    rl.extend(to_add)

            dominant_r_ix = r_color.index(max(r_color))
            for ix in rl:
                rgb_list[ix] = make_random_color(dominant_r_ix, line_variance)

            set_keyboard_rgb(rgb_list)

            sleep( log1p( 0.3 / ( abs(6-i)+1 ) ) )

            # if interval == count-1 and i == 6:
            #   break

if __name__ == '__main__':
    solid_color(0,0,0)
    write_to_file('brightness', '255')
    random_burst(secs=1, sparseness=15)
    random_burst(secs=1, sparseness=9)
    random_burst(secs=1, sparseness=5)
    random_burst(secs=1, sparseness=2)
    random_burst(secs=1, sparseness=1)
    random_burst(secs=1)
    # random_burst(secs=2, bright=True)
    # random_burst(secs=2)
    r_wipe(count=3)
    monochrome_noise(38,207,64, secs=3, variety=128)
    write_to_file('brightness', '128')
    sleep(0.2)
    write_to_file('brightness', '64')
    sleep(0.2)
    write_to_file('brightness', '32')
