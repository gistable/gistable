"""
From the man page for ssh:

     -f      Requests ssh to go to background just before command execution.  This is useful if ssh is going to ask 
             for passwords or passphrases, but the user wants it in the background.  This implies -n.  The recommended way 
             to start X11 programs at a remote site is with something like ssh -f host xterm.

             If the ExitOnForwardFailure configuration option is set to “yes”, then a client started with -f will wait 
             for all remote port forwards to be successfully established before placing itself in the background.

So using "-f -o ExitOnForwardFailure=yes" will give us an ssh command that will immediately exit, with 
return status 0 if the tunnel was successfully setup, and nonzero return status otherwise.

The only problem is that there is no way to tell what the pid of the backgrounded ssh process is, so we need
to use psutil to find the pid of the process with the matching command line string.

For a key-based connection, it's probably a good idea to use "-o BatchMode=yes" to avoid password prompts etc.

Finally, we should investigate the pair of options "-o ServerAliveInterval=5 -o ServerAliveCountMax=1" which
provide a sort of "heartbeat" to make sure that the ssh connection stays live.

:: Testing ::

In one xterm, start up the tunnel:

    [carlo@localhost ~]$ python tunnel.py 
    made the tunnel...
    terminated the tunnel

In another xterm, try to start a second tunnel on the same port:

    [carlo@localhost ~]$ python tunnel.py 
    :-(
    Error creating tunnel: 255 :: ['bind: Address already in use\n', 'channel_setup_fwd_listener: cannot listen to port: 5901\n', 'Could not request local forwarding.\n']

In this way we pick up the reason for the tunnel failing to start.
"""


import os
import psutil
import subprocess
import time

# Current ssh tunnel command in the launcher:
#
# tunnel_cmd = sshBinary + " -i " + tunnelPrivateKeyFileName + " -c " + self.cipher + " " \
#     "-t -t " \
#     "-oStrictHostKeyChecking=no " \
#     "-L " + localPortNumber + ":" + remoteHost + ":" + remotePortNumber + " -l " + tunnelUsername + " " + tunnelServer

def create_tunnel(tunnel_cmd):
    ssh_process = subprocess.Popen(tunnel_cmd,  universal_newlines=True,
                                                shell=True,
                                                stdout=subprocess.PIPE,
                                                stderr=subprocess.STDOUT,
                                                stdin=subprocess.PIPE)

    # Assuming that the tunnel command has "-f" and "ExitOnForwardFailure=yes", then the 
    # command will return immediately so we can check the return status with a poll().

    while True:
        p = ssh_process.poll()
        if p is not None: break
        time.sleep(1)

    if p == 0:
        # Unfortunately there is no direct way to get the pid of the spawned ssh process, so we'll find it
        # by finding a matching process using psutil.

        current_username = psutil.Process(os.getpid()).username
        ssh_processes = [proc for proc in psutil.get_process_list() if proc.cmdline == tunnel_cmd.split() and proc.username == current_username]

        if len(ssh_processes) == 1:
            return ssh_processes[0]
        else:
            raise RuntimeError, 'multiple (or zero?) tunnel ssh processes found: ' + str(ssh_processes) 
    else:
        raise RuntimeError, 'Error creating tunnel: ' + str(p) + ' :: ' + str(ssh_process.stdout.readlines())



# A quick test:

tunnel_cmd = 'ssh -i key.pem -o BatchMode=yes -o ServerAliveInterval=1 -o ServerAliveCountMax=5 -f -o ExitOnForwardFailure=yes -N -L 5901:localhost:5901 user@server'

try:
    ssh_tunnel_process = create_tunnel(tunnel_cmd)

    print 'made the tunnel...'
    time.sleep(5)

    ssh_tunnel_process.terminate()
    print 'terminated the tunnel'
except RuntimeError as e:
    print ":-("
    print e.message
