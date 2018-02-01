import serial
import datetime
from pymongo import MongoClient

port = serial.Serial('/dev/ttyAMA0', baudrate=9600, timeout=2.0)
client = MongoClient('172.31.150.230')


def read_pm_line(_port):
    rv = b''
    while True:
        ch1 = _port.read()
        if ch1 == b'\x42':
            ch2 = _port.read()
            if ch2 == b'\x4d':
                rv += ch1 + ch2
                rv += _port.read(28)
                return rv


loop = 0
rcv_list = []
while True:
    try:
        rcv = read_pm_line(port)
        res = {'timestamp': datetime.datetime.now(),
               'apm10': rcv[4] * 256 + rcv[5],
               'apm25': rcv[6] * 256 + rcv[7],
               'apm100': rcv[8] * 256 + rcv[9],
               'pm10': rcv[10] * 256 + rcv[11],
               'pm25': rcv[12] * 256 + rcv[13],
               'pm100': rcv[14] * 256 + rcv[15],
               'gt03um': rcv[16] * 256 + rcv[17],
               'gt05um': rcv[18] * 256 + rcv[19],
               'gt10um': rcv[20] * 256 + rcv[21],
               'gt25um': rcv[22] * 256 + rcv[23],
               'gt50um': rcv[24] * 256 + rcv[25],
               'gt100um': rcv[26] * 256 + rcv[27]
               }
        # print('===============\n'
        #       'PM1.0(CF=1): {}\n'
        #       'PM2.5(CF=1): {}\n'
        #       'PM10 (CF=1): {}\n'
        #       'PM1.0 (STD): {}\n'
        #       'PM2.5 (STD): {}\n'
        #       'PM10  (STD): {}\n'
        #       '>0.3um     : {}\n'
        #       '>0.5um     : {}\n'
        #       '>1.0um     : {}\n'
        #       '>2.5um     : {}\n'
        #       '>5.0um     : {}\n'
        #       '>10um      : {}'.format(res['apm10'], res['apm25'], res['apm100'],
        #                                res['pm10'], res['apm25'], res['pm100'],
        #                                res['gt03um'], res['gt05um'], res['gt10um'],
        #                                res['gt25um'], res['gt50um'], res['gt100um']))
        rcv_list.append(res.copy())
        loop += 1
        if loop == 10:
            client.air.pm.insert_many(rcv_list)
            print('Logged to database. {} documents totally.'.format(len(rcv_list)))
            rcv_list.clear()
            loop = 0
    except KeyboardInterrupt:
        break
