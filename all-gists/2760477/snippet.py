from fabric.api import *
from fabric.contrib.console import confirm
from local_settings import remote_user
from time import time
import subprocess, shlex, atexit, time
from settings import DATABASES
from os import remove

env.use_ssh_config = True
env.context = 'local'
tunnels = []
local_db = DATABASES['default']

class SSHTunnel:
    def __init__(self, bridge_user, bridge_host, dest_host, bridge_port=22, dest_port=22, local_port=2022, timeout=15):
        self.local_port = local_port
        cmd = 'ssh -vAN -L %d:%s:%d %s@%s' % (local_port, dest_host, dest_port, bridge_user, bridge_host)
        self.p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        start_time = time.time()
        atexit.register(self.p.kill)
        while not 'Entering interactive session' in self.p.stderr.readline():
            if time.time() > start_time + timeout:
                raise "SSH tunnel timed out"
    def entrance(self):
        return 'localhost:%d' % self.local_port

@task
def live():
    env.user = 'ops'
    prod = SSHTunnel(remote_user, 'bastion.alleyinteractive.com', 'prod.alleyinteractive.com')
    env.hosts = [prod.entrance()]
    env.context = 'live'
    env.directory = '/usr/share/django/alleyinteractive/alleyinteractive'
    env.db_config = DATABASES['default']