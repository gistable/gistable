# This is how I ensure a Python script is launched as root, and automatically
# call 'sudo' to re-launch it as root if not.

# I found it useful to check the parameters are valid *before* re-launching as
# root, so I don’t have to enter the sudo password if there is a problem with
# the parameters, or I just want the help message.


import os
import sys

# At this point we may be running as root or as another user
# - Check the parameters are valid - show an error if not
# - Show the help message if requested
# Don't do any work or anything time-consuming here as it will run twice

if os.geteuid() != 0:
    # os.execvp() replaces the running process, rather than launching a child
    # process, so there's no need to exit afterwards. The extra "sudo" in the
    # second parameter is required because Python doesn't automatically set $0
    # in the new process.
    os.execvp("sudo", ["sudo"] + sys.argv)

# Now we are definitely running as root
# - Make the changes to the system settings (e.g. Apache config)