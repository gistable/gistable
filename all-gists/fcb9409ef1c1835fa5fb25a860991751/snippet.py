import machine
import socket
import ure

RELAYS = [machine.Pin(i, machine.Pin.OUT) for i in (12, 13, 14, 15)]

def getPinStatus():
  return RELAYS

def setPin(pin, value):
  RELAYS[int(pin)].value(int(value))  
  return "PIN %s set to %s" % (pin, value)
  
def parseURL(url):
  #PARSE THE URL AND RETURN THE PATH AND GET PARAMETERS
  parameters = {}
  
  path = ure.search("(.*?)(\?|$)", url) 
  
  while True:
    vars = ure.search("(([a-z0-9]+)=([a-z0-8.]*))&?", url)
    if vars:
      parameters[vars.group(2)] = vars.group(3)
      url = url.replace(vars.group(0), '')
    else:
      break

  return path.group(1), parameters

def buildResponse(response):
  # BUILD DE HTTP RESPONSE HEADERS
  return '''HTTP/1.0 200 OK\r\nContent-type: text/html\r\nContent-length: %d\r\n\r\n%s''' % (len(response), response)
    
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

s = socket.socket()
s.bind(addr)
s.listen(1)

print('listening on', addr)

while True:
    cl, addr = s.accept()
    print('client connected from', addr)
    request = str(cl.recv(1024))
    print("REQUEST: ", request)

    obj = ure.search("GET (.*?) HTTP\/1\.1", request)
    print(obj.group(1))
    
    if not obj:
      cl.send(buildResponse("INVALID REQUEST"))
    else:
      path, parameters = parseURL(obj.group(1))
      if path.startswith("/getPinStatus"):
        cl.send(buildResponse("RELAY STATUS:\n%s" % "\n".join([str(x.value()) for x in getPinStatus()])))
        
      elif path.startswith("/setPinStatus"):
        pin = parameters.get("pin", None)
        value= parameters.get("value", None)
        
        cl.send(buildResponse("SET RELAY:\n%s" % setPin(pin, value)))
      else:
        cl.send(buildResponse("UNREGISTERED ACTION\r\nPATH: %s\r\nPARAMETERS: %s" % (path, parameters)))
        
    cl.close()