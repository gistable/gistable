# to use this, set REALM to your KRB realm, and create keytabs for each user in
# /etc/security/keystabs/<username>.jupyter.keytab
# 
# Save this file in your site-packages directory as krbspawner.py
# 
# then in /etc/jupyterhub_config.py, set:
#
#    c.JupyterHub.spawner_class = 'krbspawner.KerberosSpawner'


from jupyterhub.spawner import LocalProcessSpawner
from jupyterhub.traitlets import Command
from jupyterhub.utils import random_port
from subprocess import Popen
from tornado import gen
import pipes

REALM='EXAMPLE.COM'

class KerberosSpawner(LocalProcessSpawner):

    @gen.coroutine
    def start(self):
        """Start the process"""
        if self.ip:
            self.user.server.ip = self.ip
        self.user.server.port = random_port()
        cmd = []
        env = self.env.copy()
    
        cmd.extend(self.cmd)
        cmd.extend(self.get_args())
    
        self.log.info("Spawning %s", ' '.join(pipes.quote(s) for s in cmd))
        kinit = ['kinit', '-t',
                '/etc/security/keytabs/%s.jupyter.keytab' % self.user.name,
                '%s@%s' % (self.user.name, REALM)]
        Popen(kinit, preexec_fn=self.make_preexec_fn(self.user.name)).wait()
        self.proc = Popen(cmd, env=env,
            preexec_fn=self.make_preexec_fn(self.user.name),
        )
        self.pid = self.proc.pid
