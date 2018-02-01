#!/usr/bin/env python3

__author__ = 'Konrad Strack'
__copyright__ = 'Copyright 2014, Konrad Strack'
__license__ = 'MIT'

from math import log10

import sys
import subprocess


def get_backlight():
    return float(subprocess.check_output(["xbacklight",  "-get"]))

def set_backlight(backlight):
    subprocess.call(["xbacklight", "-set", str(backlight)])

def backlight_to_step(backlight, backlight_min, backlight_max, steps):
    x_min = log10(backlight_min)
    x_max = log10(backlight_max)
    return round(log10(backlight) / (x_max - x_min) * steps)

def step_to_backlight(step, backlight_min, backlight_max, steps):
    x_min = log10(backlight_min)
    x_max = log10(backlight_max)
    x = step / steps * (x_max - x_min)

    backlight = round(max(min(10 ** x, backlight_max), backlight_min))
    return backlight


if __name__ == "__main__":

    backlight_min = 2
    backlight_max = 100

    steps = 20

    if len(sys.argv) < 2 or sys.argv[1] not in ["-inc", "-dec"]:
        print("usage:\n\t{0} -inc / -dec".format(sys.argv[0]))
        sys.exit(0)

    current_backlight = get_backlight()
    current_step = backlight_to_step(current_backlight, backlight_min, backlight_max, steps)

    action = sys.argv[1]
    if action == "-inc":
        new_step = current_step + 1
    elif action == "-dec":
        new_step = current_step - 1

    new_backlight = step_to_backlight(new_step, backlight_min, backlight_max, steps)

    print("Current backlight: {0}\nChanging to: {1}".format(current_backlight, new_backlight))
    set_backlight(new_backlight)
