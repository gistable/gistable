import struct
import sys
import time
import json
from struct import *
from twisted.web import server, resource
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from twisted.application.internet import MulticastServer


user_pw = '0000' # default is '0000'

code_login = 0xfffd040d
code_total_today = 0x54000201
code_spot_ac_power = 0x51000201

src_serial = 987193143 # = 37 5F D7 3A (intel format, little endian)
dst_serial = 304913813 # = 95 9D 2C 12 (intel format, little endian)

comm_port = 9522
comm_dst = '192.168.2.103'


def get_encoded_pw(password):
    # user=0x88, install=0xBB
    encpw=[0x88,0x88,0x88,0x88,0x88,0x88,0x88,0x88,0x88,0x88,0x88,0x88]
    for index in range(min(len(encpw), len(password))):
        encpw[index] = encpw[index] + ord(password[index])
        
    ret = ""
    for ch in encpw:
        ret = ret + hex(ch).replace('0x','')
    return ret

cmd_login = '534d4100000402a000000001003a001060650ea0ffffffffffff00017800%s00010000000004800c04fdff07000000840300004c20cb5100000000%s00000000' % (struct.pack('<I', src_serial).encode('hex'), get_encoded_pw(user_pw))
cmd_logout = '534d4100000402a00000000100220010606508a0ffffffffffff00037800%s000300000000d7840e01fdffffffffff00000000' % (struct.pack('<I', src_serial).encode('hex'))
cmd_query_total_today = '534d4100000402a00000000100260010606509e0b500%s00007800%s000000000000f1b10002005400002600ffff260000000000' % (struct.pack('<I', dst_serial).encode('hex'), struct.pack('<I', src_serial).encode('hex'))
cmd_query_spot_ac_power = '534d4100000402a00000000100260010606509e0b500%s00007800%s00000000000081f00002005100002600ffff260000000000' % (struct.pack('<I', dst_serial).encode('hex'), struct.pack('<I', src_serial).encode('hex'))

sma_data = {}

query_list = []
rea = 0

class MulticastClientUDP(DatagramProtocol):

   def datagramReceived(self, datagram, address):
      global sma_data, data_available
      data = datagram.encode('hex')
      print "received %d bytes " % len(datagram)          
      print "data: " + data
      code = get_code(datagram)      
      print "code: %d" % code
      if code == code_login:
         print "received package code: login"
         send_command(cmd_query_total_today)
      if code == code_total_today:
         print "received package code: total, today power data"
         total = get_long_value_at(datagram, 62)
         today = get_long_value_at(datagram, 78)
         print "total: %d" % total
         print "today: %d" % today
         sma_data['total'] = total
         sma_data['today'] = today
         send_command(cmd_query_spot_ac_power)
      if code == code_spot_ac_power:
         print "received package code: spot ac power"
         value = get_long_value_at(datagram, 62)
         if value == 0x80000000:
            value = 0
         print value
         sma_data['spotacpower'] = value
         output_data = json.dumps(sma_data)
         print output_data
         out = open('sma_data.json','w')
         out.write(output_data)
         out.close()
         reactor.stop()


def send_command(cmd):
   print "sending command: %s" % cmd
   data = cmd.decode('hex')
   rea.write(data, (comm_dst, comm_port))
   
def get_code(data):
   print data[42:46].encode('hex')
   c = unpack('I', data[42:46])
   return c[0]   

def get_long_value_at(data, index):
   v = unpack('I', data[index:index+4])
   return v[0]

def callfunc(x):
    print "stopping reactor"
    reactor.stop()
    
rea = reactor.listenUDP(0, MulticastClientUDP())
_DelayedCallObj = reactor.callLater(5, callfunc, "callfunc called after 4 sec")
send_command(cmd_login)
reactor.run()
