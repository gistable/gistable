#!/usr/bin/env python

# Python port of the HiTechnic HTWay for ev3dev
# Copyright (c) 2014-2015 G33kDude, David Lechner
# HiTechnic HTWay is Copyright (c) 2010 HiTechnic


import itertools
import os
import struct
import time
import pyudev

# loop interval in seconds
WAIT_TIME = 0.008

# ratio of wheel size compared to NXT 1.0
WHEEL_RATIO_NXT1 = 1.0 # 56mm
WHEEL_RATIO_NXT = 0.8 # 43.2mm (same as EV3)
WHEEL_RATIO_RCX = 1.4 # 81.6mm

# These are the main four balance constants, only the gyro constants
# are relative to the wheel size. KPOS and KSPEED are self-relative to
# the wheel size.
KGYROANGLE = 7.5
KGYROSPEED = 1.15
KPOS = 0.07
KSPEED = 0.1

# This constant aids in drive control. When the robot starts moving
# because of user control, this constant helps get the robot leaning in
# the right direction. Similarly, it helps bring robot to a stop when
# stopping.
KDRIVE = -0.02

# Power differential used for steering based on difference of target
# steering and actual motor difference.
KSTEER = 0.25

# If robot power is saturated (over +/- 100) for over this time limit
# then robot must have fallen.  In seconds.
TIME_FALL_LIMIT = 0.5

# Gyro offset control
# The HiTechnic gyro sensor will drift with time.  This constant is
# used in a simple long term averaging to adjust for this drift.
# Every time through the loop, the current gyro sensor value is
# averaged into the gyro offset weighted according to this constant.
EMAOFFSET = 0.0005

class Gyro:
    @staticmethod
    def get_gyro():
        devices = list(pyudev.Context().list_devices(subsystem='lego-sensor') \
                .match_property("LEGO_DRIVER_NAME", EV3Gyro.DRIVER_NAME) \
                .match_property("LEGO_DRIVER_NAME", HTGyro.DRIVER_NAME))

        if not devices:
            raise Exception('Gyro not found')

        if devices[0].attributes['driver_name'] == EV3Gyro.DRIVER_NAME:
            return EV3Gyro(devices[0])
        elif devices[0].attributes['driver_name'] == HTGyro.DRIVER_NAME:
            return HTGyro(devices[0])

    def __init__(self, device):
        self.device = device
        self.value0 = open(os.path.join(self.device.sys_path, 'value0'), 'r', 0)
        self.offset = 0.0
        self.angle = 0.0

    def calibrate(self):
        self.angle = 0.0
        total = 0
        for i in range(10):
            total += self.get_rate()
            time.sleep(0.01)
        average = total / 10.0
        self.offset = average - 0.1

    def set_mode(self, value):
        with open(os.path.join(self.device.sys_path, 'mode'), 'w') as f:
            f.write(str(value))

    def get_rate(self):
        self.value0.seek(0)
        return int(self.value0.read())


class EV3Gyro(Gyro):
    DRIVER_NAME = 'lego-ev3-gyro'

    def __init__(self, device):
        Gyro.__init__(self, device)
        self.set_mode("GYRO-RATE")

    def get_data(self, interval):
        gyro_raw = self.get_rate()
        self.offset = EMAOFFSET * gyro_raw + (1 - EMAOFFSET) * self.offset
        speed = (gyro_raw - self.offset)
        self.angle += speed * interval
        return speed, self.angle

class HTGyro(Gyro):
    DRIVER_NAME = 'ht-nxt-gyro'

    def __init__(self, device):
        Gyro.__init__(self, device)

    def get_data(self, interval):
        gyro_raw = self.get_rate()
        self.offset = EMAOFFSET * gyro_raw + (1 - EMAOFFSET) * self.offset
        speed = (gyro_raw - self.offset) * 400.0 / 1953.0
        self.angle += speed * interval
        return speed, self.angle


class EV3Motor:
    def __init__(self, which=0):
        devices = list(pyudev.Context().list_devices(subsystem='tacho-motor') \
                .match_attribute('driver_name', 'lego-ev3-l-motor'))

        if which >= len(devices):
            raise Exception("Motor not found")

        self.device = devices[which]
        self.pos = open(os.path.join(self.device.sys_path, 'position'), 'r+',
                 0)
        self.duty_cycle_sp = open(os.path.join(self.device.sys_path,
                 'duty_cycle_sp'), 'w', 0)

        self.reset()

    def reset(self):
        self.set_pos(0)
        self.set_duty_cycle_sp(0)
        self.send_command("run-direct")
    def get_pos(self):
        self.pos.seek(0)
        return int(self.pos.read())

    def set_pos(self, new_pos):
        return self.pos.write(str(int(new_pos)))

    def set_duty_cycle_sp(self, new_duty_cycle_sp):
        return self.duty_cycle_sp.write(str(int(new_duty_cycle_sp)))

    def send_command(self, new_mode):
        with open(os.path.join(self.device.sys_path, 'command'),
                 'w') as command:
            command.write(str(new_mode))

class EV3Motors:
    def __init__(self, left=0, right=1):
        self.left = EV3Motor(left)
        self.right = EV3Motor(right)
        self.pos = 0.0
        self.speed = 0.0
        self.diff = 0
        self.target_diff = 0
        self.drive = 0
        self.steer = 0
        self.prev_sum = 0
        self.prev_deltas = [0,0,0]

    def get_data(self, interval):
        left_pos = self.left.get_pos()
        right_pos = self.right.get_pos()

        pos_sum = right_pos + left_pos
        self.diff = left_pos - right_pos

        delta = pos_sum - self.prev_sum
        self.pos += delta

        self.speed = (delta + sum(self.prev_deltas)) / (4 * interval)

        self.prev_sum = pos_sum
        self.prev_deltas = [delta] + self.prev_deltas[0:2]

        return self.speed, self.pos

    def steer_control(self, power, steering, interval):
        self.target_diff += steering * interval
        power_steer = KSTEER * (self.target_diff - self.diff)
        power_left = max(-100, min(power + power_steer, 100))
        power_right = max(-100, min(power - power_steer, 100))
        return power_left, power_right


def main():
    wheel_ratio = WHEEL_RATIO_RCX

    gyro = Gyro.get_gyro()
    gyro.calibrate()
    print "balancing in ..."
    for i in range(5, 0, -1):
        print i
        os.system("beep -f 440 -l 100")
        time.sleep(1)
    print 0
    os.system("beep -f 440 -l 1000")
    time.sleep(1)
    motors = EV3Motors()
    start_time = time.time()
    last_okay_time = start_time
    avg_interval = 0.0055
    for loop_count in itertools.count():
        gyro_speed, gyro_angle = gyro.get_data(avg_interval)
        motors_speed, motors_pos = motors.get_data(avg_interval)
        #print gyro_speed, gyro_angle, motors_speed, motors_pos
        motors_pos -= motors.drive * avg_interval
        motors.pos = motors_pos

        power = (KGYROSPEED * gyro_speed
                + KGYROANGLE * gyro_angle) \
                / wheel_ratio \
                + KPOS * motors_pos \
                + KDRIVE * motors.drive \
                + KSPEED * motors_speed

        left_power, right_power = motors.steer_control(power, 0, avg_interval)

        #print left_power, right_power

        motors.left.set_duty_cycle_sp(left_power)
        motors.right.set_duty_cycle_sp(right_power)

        time.sleep(WAIT_TIME)


        now_time = time.time()
        avg_interval = (now_time - start_time) / (loop_count+1)

        if abs(power) < 100:
            last_okay_time = now_time
        elif now_time - last_okay_time > TIME_FALL_LIMIT:
            break

    motors.left.send_command('reset')
    motors.right.send_command('reset')

if __name__ == "__main__":
    main()
