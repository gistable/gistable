#import the required binaries and namespaces
import clr
clr.AddReference("WebsocketClient.exe")
from WebsocketClient import *

#Make WebSocket connection to target using the supplied Origin and check if it sends messages like it does for valid sessions
def check_conn(origin):
    print "Testing origin - " + origin
    ws = SyncWebsockClient()
    ws.Connect("ws://tatgetapp.com/ws", origin, "SessionID=KSDI2923EWE9DJSDS01212")
    ws.Send("first message to send")
    msg = ws.Read()
    ws.Close()
    if msg == "message that is part of valid session":
      print "Connection successful!!"
      return True
    else:
      return False

#Loop through every possible address in the IP address namespace and check if it is accepted as a valid Origin
def check_nw():
  for nws in ["192.168.0.0/16", "172.16.0.0/12", "10.0.0.0/8"]:
    for ip in Tools.NwToIp(nws):
      if check_conn("http://" + ip):
        return

check_nw()