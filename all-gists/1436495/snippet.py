from twisted.internet import reactor, defer, endpoints, task, stdio
from twisted.conch.client import default, options, direct
from twisted.conch.error import ConchError
from twisted.conch.ssh import session, forwarding, channel
from twisted.conch.ssh import connection, common
from twisted.python import log, usage
import signal
import tty
import struct
import fcntl
import getpass
import cmd
import shlex
import sys
import os


class ClientOptions(options.ConchOptions):
    synopsis = """Usage:   sshx [options] host [command]"""
    longdesc = ("sshx is a SSHv2 client that allows logging into a remote "
                "machine, executing commands, and provides a command shell "
                "for dynamically reconfiguring session parameters.")

    optParameters = [['escape', 'e', '~'],
                      ['localforward', 'L', None, 'listen-port:host:port   Forward local port to remote address'],
                      ['remoteforward', 'R', None, 'listen-port:host:port   Forward remote port to local address'],
                     ]

    optFlags = [['null', 'n', 'Redirect input from /dev/null.'],
                 ['fork', 'f', 'Fork to background after authentication.'],
                 ['tty', 't', 'Tty; allocate a tty even if command is given.'],
                 ['notty', 'T', 'Do not allocate a tty.'],
                 ['noshell', 'N', 'Do not execute a shell or command.'],
                 ['subsystem', 's', 'Invoke command (mandatory) as SSH2 subsystem.'],
                ]

    #zsh_altArgDescr = {"foo":"use this description for foo instead"}
    #zsh_multiUse = ["foo", "bar"]
    #zsh_mutuallyExclusive = [("foo", "bar"), ("bar", "baz")]
    #zsh_actions = {"foo":'_files -g "*.foo"', "bar":"(one two three)"}
    zsh_actionDescr = {"localforward":"listen-port:host:port",
                       "remoteforward":"listen-port:host:port"}
    zsh_extras = ["*:command: "]

    localForwards = []
    remoteForwards = []

    def opt_escape(self, esc):
        "Set escape character; ``none'' = disable"
        if esc == 'none':
            self['escape'] = None
        elif esc[0] == '^' and len(esc) == 2:
            self['escape'] = chr(ord(esc[1])-64)
        elif len(esc) == 1:
            self['escape'] = esc
        else:
            sys.exit("Bad escape character '%s'." % esc)

    def opt_localforward(self, f):
        "Forward local port to remote address (lport:host:port)"
        localPort, remoteHost, remotePort = f.split(':') # doesn't do v6 yet
        localPort = int(localPort)
        remotePort = int(remotePort)
        self.localForwards.append((localPort, (remoteHost, remotePort)))

    def opt_remoteforward(self, f):
        """Forward remote port to local address (rport:host:port)"""
        remotePort, connHost, connPort = f.split(':') # doesn't do v6 yet
        remotePort = int(remotePort)
        connPort = int(connPort)
        self.remoteForwards.append((remotePort, (connHost, connPort)))

    def parseArgs(self, host, *command):
        self['host'] = host
        self['command'] = ' '.join(command)


class SSHListenClientForwardingChannel(forwarding.SSHListenClientForwardingChannel): pass
class SSHConnectForwardingChannel(forwarding.SSHConnectForwardingChannel): pass

class KeepAlive(object):
    def __init__(self, conn):
        self.conn = conn
        self.globalTimeout = None
        self.lc = task.LoopingCall(self.sendGlobal)
        self.lc.start(300)

    def sendGlobal(self):
        d = self.conn.sendGlobalRequest("conch-keep-alive@twistedmatrix.com",
                "", wantReply = 1)
        d.addBoth(self._cbGlobal)
        self.globalTimeout = reactor.callLater(30, self._ebGlobal)

    def _cbGlobal(self, res):
        if self.globalTimeout:
            self.globalTimeout.cancel()
            self.globalTimeout = None

    def _ebGlobal(self):
        if self.globalTimeout:
            self.globalTimeout = None
            self.conn.transport.loseConnection()

def beforeShutdown(options):
    remoteForwards = options.remoteForwards
    for remotePort, hostport in remoteForwards:
        log.msg('cancelling %s:%s' % (remotePort, hostport))
        conn.cancelRemoteForwarding(remotePort)

def reConnect():
    beforeShutdown()
    conn.transport.transport.loseConnection()

def stopConnection():
    def _stop():
        try: reactor.stop()
        except: pass
    #if not options['reconnect']:
    reactor.callLater(0.1, _stop)

class SSHConnection(connection.SSHConnection):
    def __init__(self, ssh, options):
        self.ssh = ssh
        self.options = options
        connection.SSHConnection.__init__(self)

    def _do_localForwards(self, localForwards):
        for localPort, hostport in options.localForwards:
            s = reactor.listenTCP(localPort,
                    forwarding.SSHListenForwardingFactory(conn,
                        hostport,
                        SSHListenClientForwardingChannel))
            self.localForwards.append(s)

    def _do_remoteForwards(self, remoteForwards):
        for remotePort, hostport in options.remoteForwards:
            log.msg('asking for remote forwarding for %s:%s' %
                    (remotePort, hostport))
            conn.requestRemoteForwarding(remotePort, hostport)
        reactor.addSystemEventTrigger('before', 'shutdown',
                                        beforeShutdown, self.options)
    def _do_fuckedFork(self):
        if os.fork():
            os._exit(0)
        os.setsid()
        for i in range(3):
            try:
                os.close(i)
            except OSError, e:
                import errno
                if e.errno != errno.EBADF:
                    raise

    def processBacklog(self, options):
        if hasattr(self.transport, 'sendIgnore'):
            KeepAlive(self)

        if options.localForwards:
            self._do_localForwards(options.localForwards)

        if options.remoteForwards:
            self._do_remoteForwards(options.remoteForwards)

        if not options['noshell'] or options['agent']:
            self.openChannel(SSHSession(self.ssh, self, self.options))

        if options['fork']:
            self._do_fuckedFork()

    def serviceStarted(self):
        self.localForwards = []
        self.remoteForwards = {}
        if not isinstance(self, connection.SSHConnection):
            # make these fall through
            del self.__class__.requestRemoteForwarding
            del self.__class__.cancelRemoteForwarding

        self.processBacklog(self.options)

        self.ssh.connectionMade(self)

    def serviceStopped(self):
        lf = self.localForwards
        self.localForwards = []
        for s in lf:
            s.loseConnection()

        self.ssh.connectionLost(self)

    def requestRemoteForwarding(self, remotePort, hostport):
        data = forwarding.packGlobal_tcpip_forward(('0.0.0.0', remotePort))
        log.msg('requesting remote forwarding %s:%s' %(remotePort, hostport))
        try:
            yield self.sendGlobalRequest('tcpip-forward', data, wantReply=1)
        except:
            log.msg('remote forwarding %s:%s failed'%(remotePort, hostport))
            raise

        log.msg('accepted remote forwarding %s:%s' % (remotePort, hostport))
        self.remoteForwards[remotePort] = hostport
        log.msg(repr(self.remoteForwards))

    def cancelRemoteForwarding(self, remotePort):
        data = forwarding.packGlobal_tcpip_forward(('0.0.0.0', remotePort))
        self.sendGlobalRequest('cancel-tcpip-forward', data)
        log.msg('cancelling remote forwarding %s' % remotePort)
        try:
            del self.remoteForwards[remotePort]
        except:
            pass
        log.msg(repr(self.remoteForwards))

    def channel_forwarded_tcpip(self, windowSize, maxPacket, data):
        log.msg('%s %s' % ('FTCP', repr(data)))
        remoteHP, origHP = forwarding.unpackOpen_forwarded_tcpip(data)
        log.msg(self.remoteForwards)
        log.msg(remoteHP)
        if self.remoteForwards.has_key(remoteHP[1]):
            connectHP = self.remoteForwards[remoteHP[1]]
            log.msg('connect forwarding %s' % (connectHP,))
            return SSHConnectForwardingChannel(connectHP,
                                            remoteWindow = windowSize,
                                            remoteMaxPacket = maxPacket,
                                            conn = self)
        else:
            raise ConchError(connection.OPEN_CONNECT_FAILED, "don't know about that port")

#    def channel_auth_agent_openssh_com(self, windowSize, maxPacket, data):
#        if options['agent'] and keyAgent:
#            return agent.SSHAgentForwardingChannel(remoteWindow = windowSize,
#                                             remoteMaxPacket = maxPacket,
#                                             conn = self)
#        else:
#            return connection.OPEN_CONNECT_FAILED, "don't have an agent"

    def channelClosed(self, channel):
        def stopReactor():
            try: reactor.stop()
            except: pass

        log.msg('connection closing %s' % channel)
        log.msg(self.channels)
        if len(self.channels) == 1: # just us left
            log.msg('stopping connection')
            if not self.options['reconnect']:
                reactor.callLater(0.1, stopReactor)
        else:
            # because of the unix thing
            self.__class__.__bases__[0].channelClosed(self, channel)


class CmdShell(cmd.Cmd):
    prompt = 'sshx? '
    def __init__(self, ssh):
        cmd.Cmd.__init__(self)
        self.ssh = ssh

    def default(self, line):
        return cmd.Cmd.default(line)

    def emptyline(self):
        pass

    def bleet(self, s):
        return sys.stderr.write(s+'\n')

    def do_shell(self, line):
        os.system(line)

    def do_remote(self, line):
        '''remote <remote_port> <hostport>
        '''
        try:
            args = shlex.split(line)
            log.msg("do_remote(%r) -> %r"%(line, args))

            remote, hostport = int(args[1]), int(args[2])
        except:
            self.bleet("expected: 2 args, <hostport> <remoteport>")
            return
        self.ssh.conn.requestRemoteForwarding(remote, hostport)

    def do_local(self, line):
        '''local <port> <remotehost> <remoteport>
        '''
        try:
            args = shlex.split(line)
            log.msg("do_local(%r) -> %r"%(line, args))

            port, rhost, rport = int(args[1]), args[2], int(args[3])
        except:
            self.bleet("expected: 3 args, <port> <remotehost> <remoteport>")
            return
        self.ssh.conn.requestLocalForwarding(port, rhost, rport)

    def do_pwd(self, line):
        '''pwd -> "/current/working/directory"
        '''
        print os.getcwd()

    def do_stop(self, line):
        '''stop the client
        '''
        reactor.stop()

    def do_cd(self, line):
        dest = line.strip()
        if dest == '':
            dest = os.environ.get('HOME', '/')
        elif dest == '-':
            dest = self.lastcwd

        oldcwd = self.lastcwd
        try:
            self.lastcwd = os.getcwd()
            os.chdir(dest)
        except:
            self.lastcwd = oldcwd

    def do_list(self, line):
        args = shlex.split(line)
        kind = args[1]
        if kind == 'local':
            l = self.localForwards
        else:
            l = self.remoteForwards
        print repr(l)


class SSHSession(channel.SSHChannel):
    name = 'session'
    def __init__(self, ssh, conn, options):
        channel.SSHChannel.__init__(self)
        self.ssh = ssh
        self.conn = conn
        self.options = options

    def allocatePty(self):
        fd = 0
        term = os.environ['TERM']
        winsz = fcntl.ioctl(fd, tty.TIOCGWINSZ, '12345678')
        winSize = struct.unpack('4H', winsz)

        ptyReqData = session.packRequest_pty_req(term, winSize, '')
        self.conn.sendRequest(self, 'pty-req', ptyReqData)
        signal.signal(signal.SIGWINCH, self._windowResized)

    def newSessionClient(self, options):
        c = session.SSHSessionClient()
        if options['escape'] and not options['notty']:
            self.escapeMode = 1
            c.dataReceived = self.handleInput
        else:
            c.dataReceived = self.write
        c.connectionLost = lambda x=None,s=self:s.sendEOF()
        return c

    def channelOpen(self, foo):
        log.msg('session %s open' % self.id)
        options = self.options

        if options['agent']:
            d = self.conn.sendRequest(self, 'auth-agent-req@openssh.com', '', wantReply=1)
            d.addBoth(lambda x:log.msg(x))
        if options['noshell']: return
        if (options['command'] and options['tty']) or not options['notty']:
            self.ssh.rawmode.enter()

        c = self.newSessionClient(options)
        self.stdio = stdio.StandardIO(c)

        if options['subsystem']:
            self.conn.sendRequest(self, 'subsystem', \
                common.NS(options['command']))
        elif options['command']:
            if options['tty']:
                self.allocatePty()
            self.conn.sendRequest(self, 'exec', \
                common.NS(options['command']))
        else:
            if not options['notty']:
                self.allocatePty()
            self.conn.sendRequest(self, 'shell', '')
            #if hasattr(conn.transport, 'transport'):
            #    conn.transport.transport.setTcpNoDelay(1)

    def handleInput(self, char):
        #log.msg('handling %s' % repr(char))
        options = self.options
        if char in ('\n', '\r'):
            self.escapeMode = 1
            self.write(char)
        elif self.escapeMode == 1 and char == options['escape']:
            self.escapeMode = 2
        elif self.escapeMode == 2:
            self.escapeMode = 1 # so we can chain escapes together
            if char == '.': # disconnect
                log.msg('disconnecting from escape')
                stopConnection()
                return
            elif char == '\x1a': # ^Z, suspend
                def _():
                    self.ssh.rawmode.leave()
                    sys.stdout.flush()
                    sys.stdin.flush()
                    os.kill(os.getpid(), signal.SIGTSTP)
                    self.ssh.rawmode.enter()
                reactor.callLater(0, _)
                return
            elif char == 'R': # rekey connection
                log.msg('rekeying connection')
                self.conn.transport.sendKexInit()
                return
            elif char == ':': # enter command mode
                old = self.stdio
                try:
                    self.ssh.rawmode.leave()
                    try:
                        cmd = CmdShell(self)
                        cmd.cmdloop('.oO( sshx )Oo.')
                    except:
                        char = None
                        log.err("cmd.cmdloop() failed")
                    self.ssh.rawmode.enter()
                finally:
                    self.stdio = old
            elif char == '#': # display connections
                self.stdio.write('\r\nThe following connections are open:\r\n')
                channels = self.conn.channels.keys()
                channels.sort()
                for channelId in channels:
                    self.stdio.write('  #%i %s\r\n' % (channelId, str(self.conn.channels[channelId])))
                return
            if char is not None:
                self.write('~' + char)
        else:
            self.escapeMode = 0
            self.write(char)

    def dataReceived(self, data):
        self.stdio.write(data)

    def extReceived(self, t, data):
        if t==connection.EXTENDED_DATA_STDERR:
            log.msg('got %s stderr data' % len(data))
            sys.stderr.write(data)

    def eofReceived(self):
        log.msg('got eof')
        self.stdio.loseWriteConnection()

    def closeReceived(self):
        log.msg('remote side closed %s' % self)
        self.conn.sendClose(self)

    def closed(self):
        global old
        log.msg('closed %s' % self)
        log.msg(repr(self.conn.channels))

    def request_exit_status(self, data):
        global exitStatus
        exitStatus = int(struct.unpack('>L', data)[0])
        log.msg('exit status: %s' % exitStatus)

    def sendEOF(self):
        self.conn.sendEOF(self)

    def stopWriting(self):
        self.stdio.pauseProducing()

    def startWriting(self):
        self.stdio.resumeProducing()

    def _windowResized(self, *args):
        winsz = fcntl.ioctl(0, tty.TIOCGWINSZ, '12345678')
        winSize = struct.unpack('4H', winsz)
        newSize = winSize[1], winSize[0], winSize[2], winSize[3]
        self.conn.sendRequest(self, 'window-change', struct.pack('!4L', *newSize))



def handleError():
    def _stopReactor():
        try: reactor.stop()
        except: pass

    from twisted.python import failure
    global exitStatus

    exitStatus = 2
    reactor.callLater(0.01, _stopReactor)
    log.err(failure.Failure())
    raise

def extract_remote_address(address):
    if address is not None:
        if type(address) == tuple:
            host, port = address
        elif isinstance(address, basestring):
            import urlparse
            host, port = urlparse.splitnport(address, 22)
        else:
            raise ValueError("address is neither (host,port) nor host:port")
    return host, port

def get_remote_address(options):
    if '@' in options['host']:
        options['user'], options['host'] = options['host'].split('@',1)
    host = options['host']
    if not options['user']:
        options['user'] = getpass.getuser()
    if not options['port']:
        options['port'] = 22
    else:
        options['port'] = int(options['port'])
    host = options['host']
    port = options['port']

    return (host, port)

class SSH(object):
    def __init__(self, options):
        self.options = options
        self.rawmode = RawConsoleMode()

    def connect(self, address=None):
        '''connect( (host, port) )
        '''
        if address is not None:
            host,port = extract_remote_address(address)
        else:
            host,port = get_remote_address(self.options)
        strport = "tcp:host={host}:port={port}".format(host=host,port=port)

        return self.connectSSH(strport)

    @defer.inlineCallbacks
    def connectSSH(self, strport, sshConnection=None):
        if sshConnection is None:
            sshConnection = SSHConnection(self, self.options)

        #vhk = default.verifyHostKey
        vhk = lambda *a: defer.succeed(1)
        uao = default.SSHUserAuthClient(self.options['user'],
                                        self.options,
                                        sshConnection)
        d = defer.Deferred()
        factory = direct.SSHClientFactory(d, self.options, vhk, uao)

        endpoint = endpoints.clientFromString(reactor, strport)
        try:
            wp = yield endpoint.connect(factory)
        except Exception:
            def _stop():
                try: reactor.stop()
                except: pass
            reactor.callLater(0.1, _stop)
            raise
        defer.returnValue(wp)

    def connectionMade(self, conn):
        pass
    def connectionLost(self, conn):
        reactor.stop()
        pass

class RawConsoleMode(object):
    def __init__(self):
        self.in_raw_mode = False
        self.saved_mode = ''

    def leave(self):
        if not self.in_raw_mode:
            return
        fd = sys.stdin.fileno()
        tty.tcsetattr(fd, tty.TCSANOW, self.saved_mode)
        self.in_raw_mode = False

    def enter(self):
        if self.in_raw_mode:
            return

        fd = sys.stdin.fileno()
        try:
            old = tty.tcgetattr(fd)
            new = old[:]
            self.saved_mode = old
        except:
            log.msg('not a typewriter!')
            self.saved_mode = None
            return

        # iflage
        new[0] = new[0] | tty.IGNPAR
        new[0] = new[0] & ~(tty.ISTRIP|tty.INLCR|tty.IGNCR|tty.ICRNL |
                        tty.IXON | tty.IXANY | tty.IXOFF)
        if hasattr(tty, 'IUCLC'):
            new[0] = new[0] & ~tty.IUCLC

        # lflag
        new[3] = new[3] & ~(tty.ISIG | tty.ICANON | tty.ECHO | tty.ECHO |
                            tty.ECHOE | tty.ECHOK | tty.ECHONL)
        if hasattr(tty, 'IEXTEN'):
            new[3] = new[3] & ~tty.IEXTEN

        #oflag
        new[1] = new[1] & ~tty.OPOST

        new[6][tty.VMIN] = 1
        new[6][tty.VTIME] = 0

        tty.tcsetattr(fd, tty.TCSANOW, new)
        self.in_raw_mode = True

# Rest of code in "run"
conn = None
exitStatus = 0

def parse_args(args):
    args = args[1:]

    if '-l' in args: # cvs is an idiot
        i = args.index('-l')
        args = args[i:i+2]+args
        del args[i+2:i+4]

    for arg in args[:]:
        try:
            i = args.index(arg)
            if arg[:2] == '-o' and args[i+1][0]!='-':
                args[i:i+2] = [] # suck on it scp
        except ValueError:
            pass

    options = ClientOptions()
    try:
        options.parseOptions(args)
    except usage.UsageError, u:
        print 'ERROR: %s' % u
        options.opt_help()
        sys.exit(1)
    if not options.identitys:
        options.identitys = ['~/.ssh/id_rsa', '~/.ssh/id_dsa']
    return options

def main(args):
    options = parse_args(args)

    if options['log']:
        if options['logfile']:
            if options['logfile'] == '-':
                f = sys.stdout
            else:
                f = file(options['logfile'], 'a+')
        else:
            f = sys.stderr
        realout = sys.stdout
        log.startLogging(f)
        sys.stdout = realout
    else:
        log.discardLogs()

    try:
        oldUSR1 = signal.signal(signal.SIGUSR1,
                                lambda *a: reactor.callLater(0, reConnect))
    except:
        oldUSR1 = None

    try:
        ssh = SSH(options)
        ssh.connect()
        reactor.run()
        #consoleio.runWithProtocol(lambda *a: SSH(options))
    finally:
        if oldUSR1:
            signal.signal(signal.SIGUSR1, oldUSR1)
        if (options['command'] and options['tty']) or not options['notty']:
            signal.signal(signal.SIGWINCH, signal.SIG_DFL)
    if sys.stdout.isatty() and not options['command']:
        print 'Connection to %s closed.' % options['host']

    return exitStatus

if __name__ == "__main__":
    sys.exit(main(sys.argv))
