import mice

# Show an array of all servers
mice.m.getAllServers()

# Create a new server
mice.m.newServer()

# Grab the new server object (for me this was server 2)
s2 = mice.m.getServer(2)

# You can check the default configuration
mice.m.getDefaultConf()

# Then set the config you need (port is one higher than default which my server 1 was running on)
s2.setConf('port','64739')
s2.setConf('registername','Base Channel Name')
s2.setConf('welcometext','<br />Welcome to my new channel!<br />')

# Start it up!
s2.start()