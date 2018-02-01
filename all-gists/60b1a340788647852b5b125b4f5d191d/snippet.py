# coding: utf-8

'''Sending / Receiving SMS using Raspberry Pi, Soracom Air SIM and ABIT AK-020
'''

import time
import serial
import re


class Sms:

  def __init__(self):
    
    self.pattern = re.compile('\+CMGL: [0-9]+,"REC UNREAD"')

    self.serial = serial.Serial(
      '/dev/ttyUSB0', 
      460800, 
      timeout = 5, 
      xonxoff = False, 
      rtscts = False, 
      dsrdtr = False,
      bytesize = serial.EIGHTBITS, 
      parity = serial.PARITY_NONE, 
      stopbits = serial.STOPBITS_ONE
    )

    self.serial.write('ATZ\r')
    self.check_response_isok()

    self.serial.write('AT+CFUN=1\r')
    self.check_response_isok()
    
    self.serial.write('AT+CGDCONT=1,"IP","soracom.io"\r')
    self.check_response_isok()

    self.serial.write('AT+CMGF=1\r')
    self.check_response_isok()


  def __del__(self):

    self.serial.close()


  def wait_response(self):

    time.sleep(1)

    while self.serial.inWaiting() == 0:
      time.sleep(0.5)


  def check_response_isok(self):

    self.wait_response()

    r = self.serial.read(self.serial.inWaiting()).split('\r\n')

    if len(r) < 2 or r[-2] != 'OK':
      raise Exception(r)


  def check_response_isprompt(self):

    self.wait_response()

    r = self.serial.read(self.serial.inWaiting()).split('\r\n')

    if len(r) < 1 or r[-1] != '> ':
      raise Exception(r)


  def dispose_response(self):

    self.wait_response()
    self.serial.read(self.serial.inWaiting())


  def send_message(self, message, to):

    self.serial.write('AT+CMGS="%s"\r' % to)
    self.check_response_isprompt()

    self.serial.write(message + chr(26)) # CTRL-Z
    self.dispose_response()

    self.check_response_isok()


  def receive_message(self):

    self.serial.write('AT+CMGL="REC UNREAD"\r\n')

    self.wait_response()

    r = self.serial.read(self.serial.inWaiting()).split('\r\n')

    if len(r) < 2 or r[-2] != 'OK':
      raise Exception(r)

    messages = []
    is_message = False

    for line in r:

      if is_message:
        messages.append(line)

      if line and self.pattern.match(line):
        is_message = True
      else:
        is_message = False

    return messages


if __name__ == "__main__":
  sms = Sms()
  sms.send_message('Hello world!', '00000000000') # replace 00000000000 by the phone number you want to send SMS to.
  print sms.receive_message()
