# File:  fakedns.py
# Name:  Interactive CLI DNS Spoofer
# by:    @mastahyeti 
#
# based off of http://code.activestate.com/recipes/491264/

from __future__ import print_function
from gevent.event import Event
from gevent.pool import Pool
from gevent import socket
import gevent

import sys
import os

# make stdout unbuffered
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

class DNSQuery:
  def __init__(self, data):
    self.data=data
    self.dominio=''

    tipo = (ord(data[2]) >> 3) & 15   # Opcode bits
    if tipo == 0:                     # Standard query
      ini=12
      lon=ord(data[ini])
      while lon != 0:
        self.dominio+=data[ini+1:ini+lon+1]+'.'
        ini+=lon+1
        lon=ord(data[ini])

  def respuesta(self, ip):
    packet=''
    if self.dominio:
      packet+=self.data[:2] + "\x81\x80"
      packet+=self.data[4:6] + self.data[4:6] + '\x00\x00\x00\x00'   # Questions and Answers Counts
      packet+=self.data[12:]                                         # Original Domain Name Question
      packet+='\xc0\x0c'                                             # Pointer to domain name
      packet+='\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04'             # Response type, ttl and resource data length -> 4 bytes
      packet+=str.join('',map(lambda x: chr(int(x)), ip.split('.'))) # 4bytes of IP
    return packet

class DNSServer:
  def __init__(self,listen_addr='',listen_port=53):
    print("Initializing DNSServer")
    self.resolutions = {}
    self.shutting_down = Event()
    self.listen_addr = listen_addr
    self.listen_port = listen_port

  def start(self):
    print("Starting DNSServer")
    self.pool = Pool()
    self.pool.spawn(self.server)
    self.pool.spawn(self.interface)    
  
  def stop(self):
    print("\nFiring shutdown event")
    self.shutting_down.set()
    try:
      self.pool.join(timeout=2)
    except socket.timeout:
      print("Force killing greenlets")
      self.pool.kill()
  
  def interface(self):
    print("Interface spawned")
    # we want to stop when the shutting_down event is fired. duh...
    while not self.shutting_down.is_set():
      # print the current resolutions
      keys = self.resolutions.keys()
      # bring cursor to begining of line
      print(chr(8)*100)
      for i in range(len(keys)):
        print("%02d - %30s => %15s - %04d hits" % (i,keys[i],self.resolutions[keys[i]]['ip'],self.resolutions[keys[i]]['hits']))

      # show prompt
      print('domain to change: ',end='')

      #sys.stdin.flush()
      choice = None
      while choice is None and self.resolutions.keys() == keys:
        # get the user input if we can.
        try:
          socket.wait_read(sys.stdin.fileno(),timeout=.3)
          choice = sys.stdin.readline()
        except socket.timeout:
          pass
      
      if choice is not None:
        try:
          choice = int(choice)
          if choice in range(len(keys)):
            host = None
            while host is None:
              # show prompt
              val = raw_input("%s => "%keys[choice])
              #make sure its valid
              try:
                host = socket.gethostbyname(val)
              except gevent.dns.DNSError:
                print("thats an invalid name")
            # accept the change
            self.resolutions[keys[choice]]['ip'] = host
            self.resolutions[keys[choice]]['hits'] = 0

        except ValueError:
          print("you must enter the number of the domain you want to change.")

      gevent.sleep(0)
      # clear the screen
      print("\n"*100)


  def server(self):
    print("Server spawned")
    # setup socket
    udps = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udps.bind((self.listen_addr,self.listen_port))

    # keep going till we are shuttin down
    while not self.shutting_down.is_set():
      data, addr = udps.recvfrom(1024)
      p=DNSQuery(data)
      domain = p.dominio
      ip = '127.0.0.1'
      if domain in self.resolutions:
        ip = self.resolutions[domain]['ip']
        self.resolutions[domain]['hits'] += 1
      else:
        try:
          ip = socket.gethostbyname(domain)
          self.resolutions[domain] = {}
          self.resolutions[domain]['ip'] = ip
          self.resolutions[domain]['hits'] = 1
        except gevent.dns.DNSError:
          pass
      udps.sendto(p.respuesta(ip), addr)
      gevent.sleep(0)
    udps.close()

if __name__ == "__main__":
  dns_server = DNSServer()
  dns_server.start()
  try:
    while True:
      gevent.sleep(0)
  except KeyboardInterrupt:
    # this is a strange hack to make sure the interrupt is no longer firing...
    interrupt_over = False
    while not interrupt_over:
      try:
        gevent.sleep(.1)
        interrupt_over = True
      except KeyboardInterrupt:
        pass

    # kill the server
    dns_server.stop()

  print("Done!")