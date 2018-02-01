import httplib, urllib
import base64
import re

class ServerService:

   def __init__(self):
      communicatorField = deployit.getClass().getDeclaredField("communicator")
      communicatorField.setAccessible(True)
      communicator = communicatorField.get(deployit.delegate)
      configField = communicator.getClass().getDeclaredField("config")
      configField.setAccessible(True)
      self.config = configField.get(communicator)
      auth = base64.encodestring('%s:%s' % (self.config.username, self.config.password)).replace('\n','')
      #self.headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain", "Authorization": "Basic %s" % auth}
      self.headers = {"Content-type": "application/x-www-form-urlencoded", "Authorization": "Basic %s" % auth}
      self.conn = httplib.HTTPConnection( self.config.host, self.config.port )

   def gc(self):
      self.conn = httplib.HTTPConnection( self.config.host, self.config.port )
      self.conn.request("POST", '/deployit/server/gc', '', self.headers)
      response = self.conn.getresponse()
      print response.read()

   def info(self):
      self.conn = httplib.HTTPConnection( self.config.host, self.config.port )
      self.conn.request("GET", '/deployit/server/info', '', self.headers)
      response = self.conn.getresponse()
      print response.read()

   def licenseReload(self):
      self.conn = httplib.HTTPConnection( self.config.host, self.config.port )
      self.conn.request("POST", '/deployit/server/license/reload', '', self.headers)
      response = self.conn.getresponse()
      print response.read()

   def maintenanceStart(self):
      self.conn = httplib.HTTPConnection( self.config.host, self.config.port )
      self.conn.request("POST", '/deployit/server/maintenance/start', '', self.headers)
      response = self.conn.getresponse()
      x = response.read()
      return self.state()

   def maintenanceStop(self):
      self.conn = httplib.HTTPConnection( self.config.host, self.config.port )
      self.conn.request("POST", '/deployit/server/maintenance/stop', '', self.headers)
      response = self.conn.getresponse()
      x = response.read()
      return self.state()

   def shutdown(self):
      self.conn = httplib.HTTPConnection( self.config.host, self.config.port )
      self.conn.request("POST", '/deployit/server/shutdown', '', self.headers)
      response = self.conn.getresponse()
      x = response.read()

   def state(self):
      self.conn = httplib.HTTPConnection( self.config.host, self.config.port )
      self.conn.request("GET", '/deployit/server/state', '', self.headers)
      response = self.conn.getresponse()
      state = re.sub("</current-mode.*",'', re.sub(".*<current-mode>",'', response.read()) )
      return state

   def help(self, command = 'DEFAULT'):
      if command == 'state':
         print "Return information about current server state (is it RUNNING or in MAINTENANCE mode)."
      elif command == 'shutdown':
         print "Stops the server process in a graceful manner."
      elif command == 'maintenanceStop':
         print "Put server into RUNNING mode."
      elif command == 'maintenanceStart':
         print "Put server into MAINTENANCE mode (prepare for shutdown)."
      elif command == 'licenseReload':
         print "Reload and validate the license file from disk"
      elif command == 'info':
         print "Returns information about the configuration of the sever."
      elif command == 'gc':
         print "Runs the garbage collector on the repository"
      else:
         print " * state"
         print " * shutdown"
         print " * maintenanceStop"
         print " * maintenanceStart"
         print " * licenseReload"
         print " * info"
         print " * gc"
      # End if


# End Class

serverService = ServerService()
