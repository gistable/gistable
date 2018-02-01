"""
Fabric tunneling utilities
    by shn@glucose.jp

class ForwardServer and relates things are refere Robey Pointer's paramiko example.
(http://bazaar.launchpad.net/~robey/paramiko/trunk/annotate/head%3A/demos/forward.py)

usage::

    with make_tunnel('user@192.168.0.2:10022') as t:
        run('pwd')

"""

import select
import SocketServer
#import random
import threading
import hashlib
from fabric.api import env
from fabric.network import join_host_strings, normalize
from fabric.state import connections

__all__ = ['tunnel', 'make_tunnel']
VERBOSE = True


def tunnel():
    KEY = 'tunnel_hoststring'
    
    if hasattr(env, KEY):
        return make_tunnel(getattr(env, KEY))
    else:
        return NullTunnel()

    
def make_tunnel(tunnel=None, remote=None, local_port=None):
    if remote is None:
        remote = env.host_string
    username, hostname, port = normalize(remote)
    
    if local_port is None:
        #local_port = random.randint(10000, 65535)
        local_port = port_from_host(remote)
    
    client = connections[tunnel]
    
    return TunnelThread(hostname, port, local_port, client.get_transport())


def port_from_host(hoststring):
    return int(hashlib.sha1(hoststring).hexdigest()[-4:], 16) | 1024


class NullTunnel():
    def __enter__(self):
        env.tunnel = self
        return self

    def __exit__(self, *exc):
        del env['tunnel']
        pass

    def rsync_shell_option(self):
        #return ''
        return env.steppingstone


class TunnelThread(threading.Thread):
    def __init__(self, remote_host, remote_port, local_port, transport):
        threading.Thread.__init__(self)
        
        class SubHander (Handler):
            chain_host = remote_host
            chain_port = int(remote_port, 10)
            ssh_transport = transport
            
        self.local_port = local_port
        self.server = ForwardServer(('127.0.0.1', self.local_port), SubHander)
        
    def run(self):
        self.server.serve_forever()

    def __enter__(self):
        self.old_host_string = env.host_string
        env.host_string = join_host_strings(env.user, '127.0.0.1', self.local_port)
        env.host = '127.0.0.1'
        env.port = self.local_port
        
        self.start()
        
        env.tunnel = self
        
        return self

    def __exit__(self, *exc):
        if env.host_string in connections:
            connections[env.host_string].close()
            del connections[env.host_string]
        
        self.server.shutdown()
        
        env.host_string = self.old_host_string
        env.user, env.host, env.port = normalize(env.host_string)
        
        del env['tunnel']

    def rsync_shell_option(self):
        return '-e "ssh -p %d -i %s"' % (self.local_port, env.key_filename)


class ForwardServer(SocketServer.ThreadingTCPServer):
    daemon_threads = True
    allow_reuse_address = True


class Handler(SocketServer.BaseRequestHandler):
    def handle(self):
        request_peername = self.request.getpeername()
        
        try:
            chan = self.ssh_transport.open_channel('direct-tcpip',
                                                   (self.chain_host, self.chain_port),
                                                   request_peername)
        except Exception, e:
            verbose('Incoming request to %s:%d failed: %s' % (self.chain_host,
                                                              self.chain_port,
                                                              repr(e)))
            return
        if chan is None:
            verbose('Incoming request to %s:%d was rejected by the SSH server.' %
                    (self.chain_host, self.chain_port))
            return

        verbose('Connected!  Tunnel open %r -> %r -> %r' % (request_peername,
                                                            chan.getpeername(), (self.chain_host, self.chain_port)))
        while True:
            r, w, x = select.select([self.request, chan], [], [])
            if self.request in r:
                data = self.request.recv(1024)
                if len(data) == 0:
                    break
                chan.send(data)
            if chan in r:
                data = chan.recv(1024)
                if len(data) == 0:
                    break
                self.request.send(data)
        chan.close()
        self.request.close()
        verbose('Tunnel closed from %r' % (request_peername,))


def forward_tunnel(local_port, remote_host, remote_port, transport):
    # this is a little convoluted, but lets me configure things for the Handler
    # object.  (SocketServer doesn't give Handlers any way to access the outer
    # server normally.)
    class SubHander (Handler):
        chain_host = remote_host
        chain_port = remote_port
        ssh_transport = transport
    ForwardServer(('', local_port), SubHander).serve_forever()


def verbose(s):
    if VERBOSE:
        print s
