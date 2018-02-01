#!/usr/bin/env python

#Connecting to: 08:7C:BE:8F:3C:FB, address type: public
#Service <uuid=Generic Attribute handleStart=12 handleEnd=15> :
#    Characteristic <Service Changed>, hnd=0xd, supports READ INDICATE 
#    -> '\x01\x00\xff\xff'
#Service <uuid=Generic Access handleStart=1 handleEnd=11> :
#    Characteristic <Device Name>, hnd=0x2, supports READ WRITE 
#    -> 'Quintic BLE'
#    Characteristic <Appearance>, hnd=0x4, supports READ 
#    -> '\x00\x00'
#    Characteristic <Peripheral Privacy Flag>, hnd=0x6, supports READ WRITE 
#    -> '\x00'
#    Characteristic <Peripheral Preferred Connection Parameters>, hnd=0x8, supports READ 
#    -> 'd\x00\xc8\x00\x00\x00\xd0\x07'
#    Characteristic <Reconnection Address>, hnd=0xa, supports READ WRITE NO RESPONSE WRITE 
#    -> ''
#Service <uuid=fee9 handleStart=23 handleEnd=29> :
#    Characteristic <d44bc439-abfd-45a2-b575-925416129600>, hnd=0x18, supports WRITE NO RESPONSE WRITE 
#    Characteristic <d44bc439-abfd-45a2-b575-925416129601>, hnd=0x1b, supports NOTIFY 
#Service <uuid=fee8 handleStart=16 handleEnd=22> :
#    Characteristic <003784cf-f7e3-55b4-6c4c-9fd140100a16>, hnd=0x11, supports NOTIFY 
#    Characteristic <013784cf-f7e3-55b4-6c4c-9fd140100a16>, hnd=0x15, supports WRITE NO RESPONSE 


from bluepy.bluepy import btle

import time,struct,datetime

class Quintic(btle.DefaultDelegate):
    def __init__(self, deviceAddress):
        btle.DefaultDelegate.__init__(self)

        self.peripheral = btle.Peripheral(deviceAddress, btle.ADDR_TYPE_PUBLIC)
        self.peripheral.setDelegate(self)

        #self.dumpCharacteristics()

        print 'Connected'

        self.peripheral.writeCharacteristic(0x1d, struct.pack('<BB', 0x01, 0x00), withResponse=True)

        print 'Notification Enabled'

        self.set_date()

    def cmd(self, data):
        self.peripheral.writeCharacteristic(0x19, data, withResponse=False)
        print '-> Command:', data.encode('hex')
        self.waitForNotifications(5.0)

    def test_cmd(self, a, b, c):
        self.cmd(struct.pack('<BBBBBBBBBBBBBBBBBBBB', a, b, c, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0))


    def set_date(self, antilost=False, metric=True):
        dt = datetime.datetime.now()
        self.cmd(struct.pack('<BBBBBBBBBBBBBBBBBBBB',  0x5a, 0x01, 0x00,
                              dt.year - 2000, # year - 2000
                              dt.month, # month (1 = jan)
                              dt.day, # day of month
                              dt.hour, # hours
                              dt.minute, # minutes
                              dt.second, # seconds
                              0x00, 0x64, # target steps / 100, hi then lo
                              0x00, # wear position
                              0x01, # motion mode
                              0x00, # sex
                              0x00, 0x02, # fixed
                              0xa4, # "i"
                              0x46, # weight
                              0xb7, # height
                              0x80 | (0x40 if metric else 0x00) | (0x20 if antilost else 0x00)
                                    # options:
                                    # 0x01 - always off?
                                    # 0x02 - always off?
                                    # 0x04 - always off?
                                    # 0x08 - always off?
                                    # 0x10 - always off?
                                    # 0x20 - anti-lost
                                    # 0x40 - 1: metric, 0: imperial
                                    # 0x80 - always on?
                             ))

    def vibrate(self, icon=0, msg=''):
        # icon: 0 = none, 1 = ringing phone, 2 = email, 3 = penguin, 4 = phone, 5 = phone
        self.cmd(struct.pack('<BBBBB15s',  0x5a, 0x15, 0x00, icon, min(len(msg),15), msg))

    def name_alert(self, msg=''):
        # not supported on W007C
        self.cmd(struct.pack('<BBBB16s',  0x5a, 0x15, 0x00, 0x83, msg))

    def button_mode(self, on=True):
        self.cmd(struct.pack('<BBBBBBBBBBBBBBBBBBBB', 0x5a, 0x0c, 0x00, 0x04, 0x01 if on else 0x00, 0x00, 0x1e, 0x00, 
                             0,0,0,0,0,0,0,0,0,0,0,0))

    def query_firmware(self):
        self.cmd(struct.pack('<BBBBBBBBBBBBBBBBBBBB', 0x5a, 0x10, 0x00, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0))


    def query_minutes_log(self):
        self.cmd(struct.pack('<BBBBBBBBBBBBBBBBBBBB', 0x5a, 0x03, 0x00, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0))

    def query_days_log(self):
        self.cmd(struct.pack('<BBBBBBBBBBBBBBBBBBBB', 0x5a, 0x07, 0x00, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0))

    def set_reminder(self, hours, minutes, delete=False):
        self.cmd(struct.pack('<BBBBBBBBBBBBBBBBBBBB', 0x5a, 0x14, 0x00, 
                    0,
                    3, # 3 for wakeup
                    0 if delete else 1,
                    hours,
                    minutes,
                    0 if delete else 1,
                    0 if delete else 1,
                    0 if delete else 1,
                    0 if delete else 1,
                    0 if delete else 1,
                    0 if delete else 1,
                    0 if delete else 1,
                    0,
                    0,
                    0,
                    0,
                    0
                  ))


    def handleNotification(self, cHandle, data):
      if cHandle == 0x1c:
        if ord(data[0]) == 0x5b:
            if ord(data[1]) == 0x01:
                print '<- Result:', data.encode('hex')
                self.device_info(data)
            elif ord(data[1]) == 0x03 or ord(data[1]) == 0x07:
                print '<- Result:', data.encode('hex')
                if ord(data[-1]):
                    self.waitForNotifications(15.0)
                else:
                    print '    No Log?'
            elif ord(data[1]) == 0x10:
                print '<- Result:', data.encode('hex')
                self.device_info_other(data)
            elif data[6:17] == 'not support':
                print '<- Command not supported:', hex(cHandle), data.encode('hex')
            elif ord(data[1]) == 0x0c:
                print '<- Result:', data.encode('hex')
                print '    Button Mode!'
            elif ord(data[1]) == 0x14:
                print '<- Result:', data.encode('hex')
                print ' Reminder Set?'
            else:
                print '<- Unknown:', data.encode('hex'), data
        elif ord(data[0]) == 0x5a:
            print '<- Data:', data.encode('hex')
            if ord(data[1]) == 0x05:
                if len(data) == 5:
                    print '    Log ACK?'
                elif ord(data[2]) == 0x01:
                    self.log = data[3:]
                    self.logoffs = 0x01
                    self.waitForNotifications(5.0)
                elif ord(data[2]) == self.logoffs + 1:
                    self.log += data[3:]
                    self.logoffs += 1
                    self.waitForNotifications(5.0)
                elif ord(data[2]) >= 0xfe:
                    self.log += data[3:]
                    self.logoffs = 0xff
                    self.handle_log(self.log)
                    self.test_cmd(0x5b, 0x05, 0x00)
                    if ord(data[2]) == 0xfe:
                        self.waitForNotifications(5.0)
                else:
                    print '    Badlog!'
        else:
            print '<- Unexpected:', data.encode('hex')
      else:
        print '<- Message from other handle', hex(cHandle)

    def device_info(self, data):
        print '    Model:', data[-5:], 'MAC:', data[5:11].encode('hex'), 'Firmware:', ord(data[-6]) | (ord(data[-7])<<8), 'Protocol:', ord(data[12]) | (ord(data[11])<<8)

    def device_info_other(self, data):
        print '    Model:', data[-5:], 'MAC:', data[7:13].encode('hex'), 'Firmware:', ord(data[4]) | (ord(data[3])<<8), 'Protocol:', ord(data[14]) | (ord(data[13])<<8)

    def handle_log(self, log):
        (length, b, c, d, e, logtype, year, month, day, first, last, v, w, x, y, z) = struct.unpack('>HBBBBBBBBBBBBBBB', log[:17])
        date = datetime.date(year=year+2000, month=month, day=day)
        print '    Log Type:', logtype
        print '    Date:', date
        print '    First?:', first, 'Last?:', last
        data = struct.unpack('>'+('H'*(length/2)), log[17:])
        print '    Count:', sum(data[first:last]), data[first:last]
        print b, c, d, e
        print v, w, x, y, z 
        print sum(data), data

    def waitForNotifications(self, time):
        self.peripheral.waitForNotifications(time)


    def disconnect(self):
        self.peripheral.disconnect()


if __name__ == '__main__':

    from itertools import product

    # Connect by address. Use "sudo hcitool lescan" to find address.
    q = Quintic('08:7C:BE:8F:3C:FB')

    q.query_minutes_log()
    q.query_days_log()

#    for b in [0x02, 0x05, 0x06, 0x0b, 0x0e, 0x0f]:
#        for a in [0x5a, 0x5b]:
#            q.test_cmd(a, b, 0)
#            q.waitForNotifications(5.0)

#    dt = datetime.datetime.now()
#    for i in range(5, 100, 5):
#        q.set_reminder(dt.hour, dt.minute+i)

    while True:
        q.waitForNotifications(5.0)


    

    # Must manually disconnect or you won't be able to reconnect.
    q.disconnect()