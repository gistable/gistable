from microbit import *

def speed_to_output(i):
    return abs(i)*255

def motor(speed, pin_a, pin_b):
    pin_a.write_analog(speed_to_output(speed) if speed > 0 else 0)
    pin_b.write_analog(speed_to_output(speed) if speed < 0 else 0)

def drive_tank(left, right):
    motor(left, pin16, pin0)
    motor(right, pin12, pin8)

while True:
    pin1.read_analog()
    pin2.read_analog()
    in_a = pin1.read_analog() >= 250
    in_b = pin2.read_analog() >= 250

    if in_a and in_b:
        drive_tank(0.5, 0.5)
    elif not in_a and in_b:
        drive_tank(1, 0.25)
    elif in_a and not in_b:
        drive_tank(0.25, 1)
    else: # not in_a and not in_b:
        drive_tank(1.0, 1.0)