#!/usr/bin/python3
 # -*- coding: utf-8 -*
import sys
import serial
import time

def main(f, ser):
  while True:
    data = serial.to_bytes([0xA5,0x5A,0x02,0x80,0xaa])
    ser.write(data)
    res = bytearray();
    times = 0;
    while True:
      if times > 3:
        break
      count = ser.inWaiting()
      if count != 0:
        recv = ser.read(count)
        res = res+recv;

      time.sleep(0.1)
      times += 1

    #print(res)
    if len(res) == 9:
      print(res)
    else:
      pass



if __name__ == '__main__':
  # 打开串口
  try:
     ser = serial.Serial("/dev/ttyAMA0", 9600)
  except:
    print('not found or denied')
    exit(1)
  try:
      main(f, ser)
  except KeyboardInterrupt:
    if ser != None:
      ser.close()