#!/usr/bin/python2

import glob
import ircbot
import imp

# Bot scan password
password = ‘d3vsh3d0652′

# Connection informatoin
network = ‘irc.freenode.net’
port = 6667
channel = ‘#irclib’
nick = ‘PyBot’
name = ‘Python Bot’

# We’ll store the commands here
commands = {}

# Scan the “commands” directory and load the modules
def scan():
   commands.clear()
   for moduleSource in glob.glob ( ‘commands/*.py’ ):
      name = moduleSource.replace ( ‘.py’, ” ).replace ( ‘\’,
‘/’ ).split ( ‘/’ ) [ 1 ].upper()
      handle = open ( moduleSource )
      module = imp.load_module ( ‘COMMAND’, handle, ( ‘commands/’
+ moduleSource ), ( ‘.py’, ‘r’, imp.PY_SOURCE ) )
      commands [ name ] = module

# Create our bot class
class ModularBot ( ircbot.SingleServerIRCBot ):

   # Join a channel when welcomed
   def on_welcome ( self, connection, event ):
      connection.join ( channel )

   # Listen to public messages
   # If the user says our name, prefixed with “$”, then we act
   def on_pubmsg ( self, connection, event ):
      if event.arguments() [ 0 ].split() [ 0 ].upper() == ( ‘$’ +
nick.upper() ):

          # See if the user specified a valid command
          # If so, call the module
          if len ( event.arguments() [ 0 ].split() ) == 1:
             pass
          elif commands.has_key ( event.arguments() [ 0 ].split()
[ 1 ].upper() ):
             commands [ event.arguments() [ 0 ].split()
[ 1 ].upper() ].index ( connection, event )

   # Listen to CTCP messages for the scan password
   # If we get it, rescan
   def on_ctcp ( self, connection, event ):
      if event.arguments() [ 0 ] == password.upper():
         scan()

# Scan for commands
scan()

# Create the bot and run it
bot = ModularBot ( [( network, port )], nick, name )
bot.start()