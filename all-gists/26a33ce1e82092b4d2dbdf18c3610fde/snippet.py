#!/usr/bin/env python
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import sys
import argparse
from smbus import SMBus
from contextlib import contextmanager

# 
# All register ceom from
# https://github.com/torvalds/linux/blob/5924bbecd0267d87c24110cbe2041b5075173a25/drivers/hwmon/w83795.c
# 
#

ADDRESS=0x2f

NUVOTON_VENDOR_ID = 0xa3
CHIP_ID = 0x79

W83795_REG_BANKSEL = 0x00

# Fan Control Mode Selection Registers (FCMS)
W83795_REG_FCMS1 = 0x201
W83795_REG_FCMS2 = 0x208
W83795_REG_TFMR = lambda index: 0x202 + index
W83795_REG_TSS = lambda index: 0x209 + index

W83795_REG_SFIV_TEMP = lambda index: range(0x280 + index * 0x10, 0x280 + index * 0x10 + 7)
W83795_REG_SFIV_DCPWM = lambda index: range(0x288 + index * 0x10, 0x288 + index * 0x10 + 7)

W83795_REG_CTFS = lambda index: 0x268 + index

#Fan Output PWM Frequency Prescalar (FOPFP)
W83795_REG_FOPFP = lambda index: 0x218 + index
#Fan Output Nonstop Value (FONV)
W83795_REG_FONV = lambda index: 0x228 + index
#Hystersis of Temperature (HT)
W83795_REG_HT = lambda index: 0x270 + index
#Target Temperature of Temperature Inputs
W83795_TTTI = lambda index: 0x260 + index

FANS = range(0,8)
TEMPS = range(0,6)

@contextmanager
def bank(bus, value):
  prev_value = w83795_set_bank(bus, value)
  yield
  w83795_set_bank(bus, prev_value)


def w83795_set_bank(bus, bank):
  assert bank in [0,1,2,3]
  # Read current bank value
  cur_bank = bus.read_byte_data(ADDRESS, W83795_REG_BANKSEL)
  # If the bank is already set, nothing to do
  if cur_bank == bank:
    return cur_bank
  # Change the bank
  bus.write_byte_data(ADDRESS, W83795_REG_BANKSEL, bank)
  # Return previous bank value
  return cur_bank


def w83795_write(bus, reg, value):
  """
  Write into the given registry.
  """
  with bank(bus, reg >> 8):
    return bus.write_byte_data(ADDRESS, reg & 0xff, value & 0xff)


def w83795_read(bus, reg):
  """
  Read the given registry.
  """
  
  if hasattr(reg, '__iter__'):
      with bank(bus, reg[0] >> 8):
        return map(lambda r: bus.read_byte_data(ADDRESS, r & 0xff), reg)
  with bank(bus, reg >> 8):
    return bus.read_byte_data(ADDRESS, reg & 0xff)


def to_degree(val, low=0, hi=127):
  """Convert hex value to degree."""
  return 127 * val / 255


def to_perc(value):
  """Convert hex value to percentage."""
  return value * 100 / 255


def from_degree(value):
  """Convert degree to hex"""
  value = max(min(int(value) + 1,127),0)
  return (value * 255 / 127) & 0xff

def from_perc(value):
  """Convert perc to hex"""
  value = max(min(int(value) + 1,100),0)
  return (value * 255 / 100) & 0xff


def main():
  # Read arguments
  parser = argparse.ArgumentParser(description='Change SuperMicro X8 Fan Control.')
  parser.add_argument('-m', '--mode', type=str, choices=['smart', 'cruise'], help='Set the fan mode: smart or cruise. smart: to use Smart Fan mode. cruise: to use Thermal Cruise mode.')
  parser.add_argument('-p', '--pwm', type=str, help='Set Fan Duty (in percentage).')
  parser.add_argument('-t', '--temp', type=str, help='Set Temperature (in Celsius) associated to pwm.')
  parser.add_argument('-H', '--hystersis', type=int, help='Set Hystersis value in degree (0-15)')
  args = parser.parse_args()

  # Open SMBus
  try:
    bus = SMBus(0)
  except:
    print("Failed to open i2c bus (/dev/i2d-0). Make sure i2c-dev module is loaded.")
    return
  #Check if we have the right device.
  try:
    vendor = w83795_read(bus, 0xfd)
    chipid = w83795_read(bus, 0xfe)
    #debug("vendor %s, chipid %s" % (vendor, chipid))
    if vendor != NUVOTON_VENDOR_ID or chipid != CHIP_ID:
      print("unexpected vendor %s, chipid %s" % (vendor, chipid))
      return

    # Check if Smarts Fan Control is enabled
    if args.mode == 'smart':
        # Check arguments
        if not args.pwm or not args.temp:
          print('pwm and temp are required')
          return
        pwm = args.pwm.split(',')
        temp = args.temp.split(',')
        if len(pwm) != len(temp):
          print("pwm and temp must have the same number of values")
          return

        # Change Smart Fan Control value
        for i in range(0,7):
          p = pwm[i] if i < len(pwm) else pwm[-1]
          tt = temp[i] if i < len(temp) else temp[-1]
          print("Set Smart Fan Control %s%% - %sC" % (p, tt))
          for t in TEMPS:
            w83795_write(bus, W83795_REG_SFIV_DCPWM(t)[i], from_perc(p))
            w83795_write(bus, W83795_REG_SFIV_TEMP(t)[i], from_degree(tt))

        # Change Minimum PWM
        for f in FANS:
          w83795_write(bus, W83795_REG_FONV(f), from_perc(pwm[0]))
        # Change critical Temp
        for t in TEMPS:
          w83795_write(bus, W83795_REG_CTFS(t), from_degree(temp[-1]))

        # Set Smart Fan Control Mode T6FC - T1FC
        w83795_write(bus, W83795_REG_FCMS1, 0x0)
        w83795_write(bus, W83795_REG_FCMS2, 0x3f)

    elif args.mode == 'cruise':
        
        # Check arguments
        if not args.temp:
          print('temp is required')
          return
        temp = int(args.temp)

        print("Set Thermal Cruise %sC" % (temp,))
        for t in TEMPS:
          w83795_write(bus, W83795_TTTI(t), from_degree(temp))

        # Change critical Temp
        for t in TEMPS:
          w83795_write(bus, W83795_REG_CTFS(t), from_degree(80))

        # Set Thermal Cruise Mode.
        w83795_write(bus, W83795_REG_FCMS1, 0x0)
        w83795_write(bus, W83795_REG_FCMS2, 0x0)

    # Set hystersis
    if args.hystersis:
      ht = max(min(args.hystersis,15),0)
      print("Set hystersis %sC" % ht)
      # Change Smart Fan Control value
      for t in range(0,6):
        w83795_write(bus, W83795_REG_HT(t), ht)

    if args.mode or args.pwm or args.temp or args.hystersis:
      return

    # Check if Smarts Fan Control is enabled
    fcms1 = w83795_read(bus, W83795_REG_FCMS1)
    fcms2 = w83795_read(bus, W83795_REG_FCMS2) & 0xff

    # Default to show all data.
    for t in TEMPS:
      print("Temp%s to Fan mapping Relationships (T%sFMR)" % (t+1, t+1))
      tfmr = w83795_read(bus, W83795_REG_TFMR(t))
      fans= [i+1 for i in FANS if tfmr & (0x1<<i)]
      print(' '.join(['Fan%s' % i for i in fans]))

      print("Smart Fan Control Table (SFIV)")
      temp = w83795_read(bus, W83795_REG_SFIV_TEMP(t))
      print(''.join([("%sC" % to_degree(v)).rjust(6) for v in temp]))

      dcpwm = w83795_read(bus, W83795_REG_SFIV_DCPWM(t))
      print(''.join([("%s%%" % to_perc(v)).rjust(6) for v in dcpwm]))

      ttti = w83795_read(bus, W83795_TTTI(t))
      print("Thermal Cruise (TTTI): %sC" % (ttti,))

      ctfs = w83795_read(bus, W83795_REG_CTFS(t))
      print("Critical Temperature (T%sCTFS): %sC" % (t, to_degree(ctfs)))

      ht = w83795_read(bus, W83795_REG_HT(t)) & 0b1111
      print("Hysteresis (HT%s): %sC" % (t, ht))

      print('')

    for f in FANS:
      fonv = w83795_read(bus, W83795_REG_FONV(f))
      print("Fan%s Output Nonstop Value (F%sONV): %s%%" % (f+1, f+1, to_perc(fonv)))

    #for f in range(0,6):
    #  w83795_write(bus, W83795_REG_FONV(f), 50)
    #w83795_write(bus, W83795_REG_SFIV_DCPWM(0)[0], 50)
    #w83795_write(bus, W83795_REG_SFIV_TEMP(0)[0], 85)
    #w83795_write(bus, W83795_REG_SFIV_TEMP(1)[0], 85)

  finally:
    bus.close()


if __name__ == "__main__":
    main()
