#!/usr/bin/python
# pinkie.py -- Proof-of-concept IRCd written in Python

# [40] alex@theta pinkie $ grep ^class pinkie.py 
# class Pollable:
# class Timer:
# class TimerRepeat(Timer):
# class AsyncListen(Pollable):
# class AsyncLine(Pollable):
# class AsyncLoop:
# class IRCSource:
# class IRCMessage:
# class IRCModeList:
# class IRCPostOffice:
# class IRCClient(AsyncLine, IRCPostOffice):
# class IRCChannel(IRCPostOffice):
# class IRCd:

# sanity check
import sys, os
if sys.version_info.major < 3:
    print('Sorry, but pinkie.py must be run with Python >= 3.0')
    sys.exit(1)


# import ALL THE THINGS!
import socket
import select
import string
import queue
import time
import json
import traceback


# Software facts

PINKIE = { 'VERSION': 'pinkie.py-0.1',
           'AUTHOR': 'Alex Iadicicco' }


# Base pollable async object

class Pollable:
    '''
    This class forms the base of the asynchronous IO API used here
    '''

    def __init__(self):
        pass

    def alive(self):
        '''
        Indicate whether we should continue to poll for events, or if
        we should be deleted from the async loop. NOTE: only return True
        once you have finished all cleanup operations, as the async
        API does not explicitly call any sort of cleanup function upon
        deletion.
        '''
        return False

    def close(self):
        '''
        This function should close all resources the pollable is using
        and ensure that future calls to alive() will return False. Once
        this function is called, it is safe to assume that do_recv and
        do_send will never be called.
        '''
        pass

    def select_recv(self):
        '''
        Return True to be included in the list of potential readers
        given to select(). It is not bad practice to always return True.
        '''
        return False

    def select_send(self):
        '''
        Return True to be included in the list of potential writers given
        to select(). Calls to select() with potential writers tend to
        return quickly, because sockets are very frequently available
        for writing, much more so than they are for reading. Do the
        Right Thing (tm) and only return True if you actually have data
        to share.
        '''
        return False

    def fileno(self):
        '''
        This should return the file descriptor of the resource which we
        are reading from or writing to.
        '''
        return 0

    def do_recv(self):
        '''
        This function is called when the asynchronous loop detects
        that there is data ready to be read. You will not be checked
        for readable data on an async loop if you don't return true
        in select_recv().
        '''
        pass

    def do_send(self):
        '''
        This function is called when the asynchronous loop
        detects the socket is ready to write to. You will not be
        checked for a writable socket if you do not return True in
        select_send(). However, as sockets are very often writable,
        it is important to only have this function be called when data
        is ready for writing. Your select_send() function should implement
        some sort of 'data ready' logic.
        '''
        pass


# Base Timer class

class Timer:
    '''
    This class reports to the asynchronous loop the time of the next
    firing event, and provides a method for the async loop to call on
    timing events.
    '''

    def alive(self):
        ''' If false, this timer will be dropped from the async loop. '''
        return False

    def delay_for(self):
        '''
        Returns the amount of time, in seconds, until the timer is
        expected to fire a timing event.
        '''
        return 1

    def should_run(self):
        ''' Returns true if the timer should fire a timing event '''
        return False

    def run(self):
        ''' Called when the async loop detects a timing event '''
        pass


# Timer for regular, repeated callbacks

class TimerRepeat(Timer):

    def __init__(self, interval, cb):
        '''
        'interval' is a time, in seconds, to wait between each call to
        cb. cb should accept a single argument: the timer that called it.
        '''
        self.next_time = time.time() + interval
        self.interval = interval
        self.dead = False
        self.cb = cb

    def alive(self):
        return not self.dead
    def die(self):
        self.dead = True

    def delay_for(self):
        return self.next_time - time.time()

    def should_run(self):
        return time.time() >= self.next_time

    def run(self):
        self.next_time += self.interval
        self.cb(self)


# Asynchronous listeners

class AsyncListen(Pollable):
    '''
    This class provides a Pollable interface for listening sockets. When
    a connection is available, the accept_cb function is called with
    the new socket object.
    '''

    def __init__(self, sock, accept_cb):
        self.sk = sock
        self.accept_cb = accept_cb

        self.dead = False

    def alive(self):
        return not self.dead

    def close(self):
        self.sk.close()
        self.dead = True

    def select_recv(self):
        return True

    def select_send(self):
        return False

    def fileno(self):
        return self.sk.fileno()

    def do_recv(self):
        conn, addr = self.sk.accept()
        self.accept_cb(conn, addr)

    def do_send(self):
        pass


# Asynchronous Line-buffered IO, tuned for IRC

class AsyncLine(Pollable):
    '''
    This class provides a basic API for asynchronously sending and
    recieving lines over a socket stream. The entire IRC protocol is
    built off of the idea of messages encoded in lines, so such a class
    is key to a complete IRC implementation.

    It is important to note the occurrence of the .decode() and .encode()
    functions in this class. Internally, AsyncLine only deals with byte
    arrays, but as soon as data leaves/enters, it is .decode()-ed or
    .encode()-ed appropriately to a regular Python string.

    Use .line_recv() and .line_send()
    '''

    def __init__(self, sock):
        self.sk = sock

        self.sendq = b''
        self.recvq = [b'']

        self.dead = False


    def alive(self):
        return self.sk.fileno() > 0 and not self.dead

    def close(self):
        self.sk.close()
        self.dead = True


    def select_recv(self):
        return self.alive()

    def select_send(self):
        return self.alive() and len(self.sendq) > 0

    def fileno(self):
        return self.sk.fileno()


    def do_recv(self):
        try:
            s = self.sk.recv(1024)
        except socket.error:
            self.close()
            return

        if len(s) == 0:
            self.close()
            return

        s = self.recvq[-1] + s.replace(b'\r', b'')
        self.recvq = s.split(b'\n')

    def do_send(self):
        try:
            s = self.sk.send(self.sendq)
            self.sendq = self.sendq[s:]
        except socket.error:
            self.close()
            return


    def line_recv(self):
        '''
        This is an iterator function that will pop and yield each full
        line from the recvq. Incomplete data is not returned
        '''
        for line in self.recvq[:-1]:
            yield line.decode()
        self.recvq = self.recvq[-1:]

    def line_send(self, line):
        '''
        Adds a line to the sendq. 'line' should not have any
        terminators. That could cause things to break :(
        '''
        self.sendq += line.encode() + b'\r\n';


class AsyncLoop:
    '''
    This class provides a straightforward way to aggregate multiple
    asynchronous IO objects (like AsyncLine above) into a single
    group. This class will take care of polling them all.

    The only requirement for objects to be added to the loop is that
    they implement the functionality in the Pollable class.
    '''

    def __init__(self, on_error=None):
        self.pollables = []
        self.timers = []

        self.running = True

        self.on_error = on_error

    def die(self):
        self.running = False


    def add_pollable(self, p):
        self.pollables.append(p)

    def del_pollable(self, p):
        if p in self.pollables:
            p.close()
            self.pollables.remove(p)


    def add_timer(self, t):
        self.timers.append(t)

    def del_timer(self, t):
        if t in self.timers:
            self.timers.remove(t)


    def step(self):
        timeout = None

        for t in self.timers:
            if t.should_run():
                t.run()

            time = t.delay_for()
            if timeout == None or time < timeout:
                timeout = time

        r, w, x = [], [], []

        for p in self.pollables:
            if p.select_recv():
                r.append(p)
            if p.select_send():
                w.append(p)

        r, w, x = select.select(r, w, x, timeout)

        for recvr in r:
            recvr.do_recv()
        for sendr in w:
            sendr.do_send()

        for p in self.pollables:
            if not p.alive():
                self.del_pollable(p)

    def loop(self):
        if len(self.pollables) + len(self.timers) == 0:
            raise StandardError("Attempt to use AsyncLoop.loop() with no pollables or timers!")

        self.running = True

        while len(self.pollables) + len(self.timers) > 0 and self.running:
            try:
                self.step()
            except:
                if self.on_error:
                    self.on_error()


# IRC Source

class IRCSource:
    server = False

    nick = ''
    ident = ''
    host = ''

    def __init__(self, spec=None):
        if spec == None:
            return

        a = (spec + '@').split('@')
        b = (a[0] + '!').split('!')

        self.nick = b[0]
        self.ident = b[1]
        self.host = a[1]

        server = '.' in self.nick

    def __str__(self):
        if self.server:
            return self.nick
        else:
            s = [self.nick]
            if self.ident:
                s.append('!' + self.ident)
            if self.host:
                s.append('@' + self.host)
            return ''.join(s)

    def cnick(self):
        return self.nick.upper()


# IRC Messages

class IRCMessage:
    '''
    IRC is primarily a message-passing protocol. This structure parses
    message formats into a usable structure for pinkie.py
    '''

    source = None
    command = ''
    args = []


    def __init__(self, spec):
        self.raw = spec

        # is there a source parameter?
        if spec[0] == ':':
            self.source, x, spec = spec[1:].partition(' ')
            self.source = IRCSource(self.source)

        # parse the command and args
        args, x, trailing = spec.partition(' :')
        args = args.split()

        self.command = args[0].upper()
        self.args = args[1:]

        if x == ' :':
            self.args.append(trailing)


class IRCModeList:
    '''
    This class provides a straightforward interface for keeping track
    of modes, whether they be user modes or channel modes or whatever.
    '''

    def __init__(self, init_modes, mode_types, unk_cb=None):
        '''
        mode_types should be a comma-separated list of groups of mode
        chars similar in formatting to the CHANTYPES ISUPPORT parameter.
        '''
        self.mode_types = mode_types.split(',')
        self.unk_cb = unk_cb

        self.m = {}
        for m in self.mode_types[0]:
            self.m[m] = []
        for m in self.mode_types[1] + self.mode_types[2]:
            self.m[m] = None
        for m in self.mode_types[3]:
            self.m[m] = False

        self.mode(init_modes)

    def mode(self, spec, args=[]):
        action = 0

        retm, reta = '', []

        for m in spec:
            if m == '-':
                action = -1
                retm += '-'
            elif m == '+':
                action = 1
                retm += '+'

            else:
                cm, ca = '', []
                if action > 0:
                    cm, ca = self.mode_set(m, args)
                elif action < 0:
                    cm, ca = self.mode_clear(m, args)
                retm += cm
                reta += ca

        return retm, reta

    def mode_set(self, m, args=[]):
        if m in self.mode_types[0]:
            if len(args) == 0:
                return '', []

            s = args.pop(0)
            if not s in self.m[m]:
                self.m[m].append(s)
                return m, s

        elif m in self.mode_types[1] + self.mode_types[2]:
            if len(args) == 0:
                return '', []

            self.m[m] = args.pop(0)
            return m, self.m[m]

        elif m in self.mode_types[3]:
            self.m[m] = True
            return m, []

        else:
            if self.unk_cb:
                return self.unk_cb(self, 1, m, args)
            return '', []

    def mode_clear(self, m, args=[]):
        if m in self.mode_types[0]:
            if len(args) == 0:
                return

            s = args.pop(0)
            if s in self.m[m]:
                self.m[m].remove(s)
                return m, s

        elif m in self.mode_types[1] + self.mode_types[2]:
            self.m[m] = None
            return m, []

        elif m in self.mode_types[3]:
            self.m[m] = False
            return m, []

        else:
            if self.unk_cb:
                return self.unk_cb(self, -1, m, args)
            return '', []

    def get_set_flags(self):
        s = []
        for m in self.m.keys():
            if self.m[m] == True:
                s.append(m)
        return ''.join(s)

    def __getitem__(self, key):
        return self.m[key]
    def __setitem__(self, key, value):
        self.m[key] = value


# IRC Post Office: send IRC messages

class IRCPostOffice:
    '''
    This class makes it easy to format and send messages to an
    AsyncLine. Extend it with your own implementations for MAXIMUM
    MESSAGE-PASSING POWERRR.
    '''

    def numeric(self, source, num, message):
        pass
    def raw(self, message):
        pass
    def send(self, source, message):
        pass
    def privmsg(self, source, text):
        pass
    def notice(self, source, text):
        pass


# IRC Clients

class IRCClient(AsyncLine, IRCPostOffice):
    '''
    This class keeps track of details of a client connection
    '''

    DEFAULT_MODES = '+i'
    CLIENT_MODES = ',,,i'

    # :c -- waiting for handshake
    # :) -- connected, authed
    # o/ -- disconnecting
    connection_status = ':c'

    si = None
    gecos = ''

    min_args = { 'OPER': 2,
                 'NICK': 1,
                 'JOIN': 1,
                 'PART': 1,
                 'PRIVMSG': 2,
                 'NOTICE': 2,
                 'MODE': 1 }
                

    def __init__(self, ircd, sock):
        AsyncLine.__init__(self, sock)
        self.ircd = ircd 

        self.si = IRCSource()
        self.mode = IRCModeList(IRCClient.DEFAULT_MODES, IRCClient.CLIENT_MODES)

        self.ping_wait = False
        self.ping_update_times()

        self.oper = False

        self.channels = []


    def verbose(self, msg):
        if self.ircd.cfg['verbose']:
            self.debug(msg)
    def debug(self, msg):
        self.ircd.debug('    {0}: {1}'.format(self.si.nick, msg))
    def whine(self, msg):
        self.ircd.whine('    {0}: {1}'.format(self.si.nick, msg))


    def alive(self):
        return self.connection_status != 'o/'
    def die(self):
        self.connection_status = 'o/'


    def do_recv(self):
        super().do_recv()

        for line in self.line_recv():
            if len(line) == 0:
                continue

            msg = IRCMessage(line)

            self.verbose(' <- ' + line)

            if self.connection_status == ':)':
                self.msg_connected(msg)
            elif self.connection_status == ':c':
                self.msg_shake(msg)
            elif self.connection_status == 'o/':
                self.msg_disconnect(msg)

        self.ping_update_times()

        if not super().alive():
            self.debug('Link dead, closing socket')
            self.ircd.client_quit(self, 'Link dead')


    def ping_update_times(self):
        self.ping_die = time.time() + self.ircd.cfg['ping']
        self.ping_check = time.time() + self.ircd.cfg['ping'] / 2

    def ping_test(self):
        if time.time() > self.ping_die:
            self.debug('Ping timeout')
            self.ircd.client_quit(self, 'Ping timeout')
        if time.time() > self.ping_check and not self.ping_wait:
            self.debug('Sending ping challenge')
            self.raw('PING :{0}'.format(self.ircd.cfg['server_host']))
            self.ping_wait = True


    def msg_shake(self, msg):
        if msg.command == 'NICK':
            if len(msg.args) < 1:
                return

            if self.ircd.nick_acceptable(self, msg.args[0]):
                self.si.nick = msg.args[0]

        if msg.command == 'USER':
            if len(msg.args) < 4:
                return

            self.si.ident = msg.args[0]
            self.si.host = 'example.net'
            self.gecos = msg.args[-1]

        if self.si.nick != '' and self.si.ident != '':
            self.debug('Got handshake')
            if self.ircd.client_welcome(self):
                self.debug('New client is connected')
                self.connection_status = ':)'
                self.raw(':{0} MODE {0} +{1}'.format(self.si.nick, self.mode.get_set_flags()))
            else:
                self.debug('New client was denied, dying')
                self.connection_status = 'o/'


    def msg_connected(self, msg):

        if msg.command in self.min_args and len(msg.args) < self.min_args[msg.command]:
            self.ircd.numeric(self, '461', ':Not enough parameters')
            return


        if msg.command == 'PING':
            unused1, unused2, text = msg.raw.partition('PING ')
            self.raw('PONG {0}'.format(text))

        elif msg.command == 'PONG':
            self.ping_wait = False


        elif msg.command == 'LIST':
            self.ircd.burst_client_list(self)

        elif msg.command == 'VERSION':
            self.ircd.burst_client_version(self)

        elif msg.command == 'MOTD':
            self.ircd.burst_client_motd(self)


        elif msg.command == 'OPER':
            self.ircd.try_oper(self, msg.args[0], msg.args[1])

        elif msg.command == 'NICK':
            if self.ircd.nick_acceptable(self, msg.args[0]):
                self.ircd.nick_change(self, msg.args[0])

        elif msg.command == 'USER':
            self.ircd.numeric(self, '462', ':You may not reregister')


        elif msg.command == 'JOIN':
            if len(msg.args) < 1:
                self
            for chan in msg.args[0].split(','):
                self.ircd.try_join(self, chan)

        elif msg.command == 'PART':
            text = None
            if len(msg.args) > 1:
                text = msg.args[1]

            for chan in msg.args[0].split(','):
                self.ircd.try_part(self, chan, text)


        elif msg.command == 'PRIVMSG':
            self.ircd.try_privmsg(self, msg.args[0], msg.args[1])

        elif msg.command == 'NOTICE':
            self.ircd.try_notice(self, msg.args[0], msg.args[1])

        elif msg.command == 'MODE':
            if msg.args[0][0] == '#':
                # defer channel mode changes to the IRCd
                self.ircd.try_mode(self, msg.args[0], msg.args[1:])
            elif msg.args[0].upper() == self.si.nick.upper():
                if len(msg.args) > 1:
                    self.mode.mode(msg.args[1], msg.args[2:])
                self.ircd.numeric(self, '221', '+' + self.mode.get_set_flags())
            else:
                self.ircd.numeric(self, '502', ':Cannot change mode for other users')

        elif msg.command == 'TOPIC':
            if len(msg.args) == 1:
                self.ircd.send_topic(self, msg.args[0])
            else:
                self.ircd.try_topic(self, msg.args[0], msg.args[1])


        elif msg.command == 'WHO':
            


        elif msg.command == 'QUIT':
            text = 'Client quit'
            if len(msg.args) > 0:
                text = msg.args[0]

            self.ircd.client_quit(self, text)


        elif msg.command == 'CRASH':
            this_function_should_not_exist()


    def msg_disconnect(self, msg):
        self.whine('Message recieved while disconnected')


    def mode_unk_cb(self, mode, action, m, args):
        if action < 0 and m == 'o' and self.oper:
            self.oper_down()
            return 'o', []

        if action > 0 and m == 'o' and self.oper:
            return 'o', []

        return '', []


    def oper_up(self):
        self.oper = True
        self.mode.mode('o', [])

    def oper_down(self):
        self.oper = False


    def raw(self, message):
        self.verbose(' -> ' + message)
        self.line_send(message)
    def send(self, source, message):
        self.raw(':{0} {1}'.format(source, message))

    def numeric(self, source, num, message):
        self.send(source, '{0} {1} {2}'.format(num, self.si.nick, message))
    def privmsg(self, source, text):
        self.send(source, 'PRIVMSG {0} :{1}'.format(self.si.nick, text))
    def notice(self, source, text):
        self.send(source, 'NOTICE {0} :{1}'.format(self.si.nick, text))


# IRC Channel

class IRCChannel(IRCPostOffice):
    '''
    This class maintains information about a channel. It can send
    information about the channel to a client or to all of its clients.
    '''

    DEFAULT_MODES = '+nt'
    CHANNEL_MODES = 'bI,,,imnpst'

    name = None
    topic = ''
    clients = {}

    def __init__(self, ircd, name, first_client):
        self.ircd = ircd
        self.name = name

        self.clients = { first_client.si.cnick(): ['@', first_client] }
        self.mode = IRCModeList(IRCChannel.DEFAULT_MODES, IRCChannel.CHANNEL_MODES, self.mode_unk_cb)

        self.burst_client_all(first_client)


    def debug(self, line):
        self.ircd.debug('  {0}: {1}'.format(self.name, line))
    def whine(self, line):
        self.ircd.debug('  {0}: {1}'.format(self.name, line))


    def is_empty(self):
        return len(self.clients) == 0


    def has_invite(self, client):
        return True
    def has_ban(self, client):
        return False
    def has_client(self, client):
        return client.si.cnick() in self.clients
    def has_voice(self, client):
        if not client.si.cnick() in self.clients:
            return False
        return self.clients[client.si.cnick()][0] != ''


    def list_line(self, client):
        if self.mode['s'] or self.mode['p'] and not client.si.cnick() in self.clients:
            return None
        return '{0} {1} :{2}'.format(self.name, len(self.clients), self.topic)


    def burst_client_topic(self, client):
        if self.topic != '':
            self.ircd.numeric(client, '332', '{0} :{1}'.format(self.name, self.topic))
        else:
            self.ircd.numeric(client, '331', '{0} :No topic is set'.format(self.name))

    def burst_client_names(self, client):
        kind = '='
        if self.mode['p']:
            kind = '*'
        if self.mode['s']:
            kind = '@'

        names = [v[0] + v[1].si.nick for v in self.clients.values()]

        while len(names) > 0:
            s = ''
            while len(s) < 400 and len(names) > 0:
                s += names.pop(0) + ' '
            self.ircd.numeric(client, '353', '{0} {1} :{2}'.format(kind, self.name, s[:-1]))

        self.ircd.numeric(client, '366', '{0} :End of NAMES list'.format(self.name))

    def burst_client_all(self, client):
        self.send(client.si, 'JOIN {0}'.format(self.name))
        self.burst_client_topic(client)
        self.burst_client_names(client)


    def nick_change(self, client, newnick):
        if not client.si.cnick() in self.clients:
            return

        self.clients[newnick.upper()] = self.clients[client.si.cnick()]
        del self.clients[client.si.cnick()]


    def client_join(self, client):
        if client.si.cnick() in self.clients:
            return True

        if self.mode['i'] and not self.has_invite(client):
            self.ircd.numeric(client, '473', '{0} :You must be invited to {0}'.format(self.name))
            return False

        if self.has_ban(client):
            self.ircd.numeric(client, '474', '{0} :You are banned from {0}'.format(self.name))
            return False

        self.debug('Adding user ' + client.si.nick)

        self.clients[client.si.cnick()] = ['', client]
        self.burst_client_all(client)

        return True

    def client_part(self, client, text=None):
        if not client.si.cnick() in self.clients:
            return

        if text == None:
            text = client.si.cnick()

        self.debug('Parting user ' + client.si.nick)

        self.send(client.si, 'PART {0} :{1}'.format(self.name, text))
        del self.clients[client.si.cnick()]

    def client_quit(self, client, text=None):
        if not client.si.cnick() in self.clients:
            return

        if text == None:
            text = 'Client quit'

        self.debug('Quitting user ' + client.si.nick)

        self.send_excl(client.si, 'QUIT :{0}'.format(text))
        del self.clients[client.si.cnick()]


    def can_send(self, client):
        if self.mode['n'] and not self.has_client(client):
            self.ircd.numeric(client, '404', '{0} :Cannot send to channel (+n)'.format(self.name))
            return False

        if self.mode['m'] and not self.has_voice(client):
            self.ircd.numeric(client, '404', '{0} :Cannot send to channel (+m)'.format(self.name))
            return False

        return True

    def try_privmsg(self, client, text):
        if self.can_send(client):
            self.privmsg(client.si, text)

    def try_notice(self, client, text):
        if self.can_send(client):
            self.notice(client.si, text)


    def try_mode(self, client, modes, args):
        if self.prefix_get(client.si.cnick()) != '@':
            self.ircd.numeric(client, '482', '{0} :You are not channel operator'.format(self.name))
            return

        self.mode.client = client
        m, a = self.mode.mode(modes, args)

        if m != '':
            self.send(client.si, 'MODE {0} {1} {2}'.format(self.name, m, ' '.join(a)))

    def mode_unk_cb(self, mode, action, m, args):
        if len(args) == 0:
            return

        if m in 'ov':
            s = args.pop(0)
            cs = s.upper()

            if cs in self.clients:
                prefix = {'o':'@', 'v':'+'}[m]

                if action < 0:
                    self.prefix_clear(cs, prefix)
                elif action > 0:
                    self.prefix_set(cs, prefix)

                return m, [s]

            else:
                mode.client.numeric(self.ircd.si, '441', '{0} {1} :User not in channel'.format(s, self.name))

        else:
            mode.client.numeric(self.ircd.si, '472', '{0} :is an unknown mode char to me'.format(m))

        return '', []

    def send_mode(self, client):
        self.ircd.numeric(client, '324', '{0} +{1}'.format(self.name, self.mode.get_set_flags()))


    def try_topic(self, client, newtopic):
        if self.mode['t'] and self.prefix_get(client.si.cnick()) != '@':
            self.ircd.numeric(client, '482', '{0} :You are not channel operator'.format(self.name))
            return

        self.topic = newtopic
        self.send(client.si, 'TOPIC {0} :{1}'.format(self.name, self.topic))


    def prefix_get(self, cnick):
        if not cnick in self.clients:
            return ''

        p = self.clients[cnick][0]

        if len(p) == 0:
            return ''
        return p[0]

    def prefix_set(self, cnick, prefix):
        if not cnick in self.clients:
            return

        c = self.clients[cnick]

        if not prefix in c[0]:
            if prefix == '@':
                c[0] = '@' + c[0]
            elif prefix == '+':
                c[0] = c[0] + '+'

    def prefix_clear(self, cnick, prefix):
        if not cnick in self.clients:
            return

        self.clients[cnick][0] = self.clients[cnick][0].replace(prefix, '')


    def raw(self, message):
        for client in self.clients.values():
            client[1].raw(message)
    def raw_excl(self, source, message):
        for client in self.clients.values():
            if source.cnick() != client[1].si.cnick():
                client[1].raw(message)

    def send(self, source, message):
        self.raw(':{0} {1}'.format(source, message))
    def send_excl(self, source, message):
        self.raw_excl(source, ':{0} {1}'.format(source, message))

    def privmsg(self, source, text):
        self.raw_excl(source, ':{0} PRIVMSG {1} :{2}'.format(source, self.name, text))

    def notice(self, source, text):
        self.raw_excl(source, ':{0} NOTICE {1} :{2}'.format(source, self.name, text))


# The main IRCd class. One instance per thread.

class IRCd:
    '''
    An instance of this class is an instance of the IRCd. The .run()
    function is blocking. There is no way to merge the async loops of
    two IRCd's at this point
    '''

    default_cfg = { 'bind_host': '',
                    'bind_ports': [6667, 6668, 6669],

                    'net_name': 'PinkieNet',

                    'server_name': 'PinkiePy',
                    'server_host': 'pinkie.py',
                    'admin_name': 'Nobody',
                    'admin_desc': 'Nonexistent',
                    'admin_email': 'nobody@example.net',

                    'motd': ['The admin forgot to make a MOTD :o'],

                    'opers': {'aji': 'pinkie'},
                    'verbose': True,

                    'ping': 300 }

    def __init__(self, config):
        self.cfg = config

        self.opers = {}
        self.channels = {}
        self.clients = {}

        for key in self.default_cfg.keys():
            if key not in self.cfg:
                self.cfg[key] = self.default_cfg[key]

        self.guests = 0

        self.si = IRCSource()
        self.si.server = True
        self.si.nick = self.cfg['server_host']

        self.async = AsyncLoop(self.on_error)
        self.listening = []
        self.make_listeners()
        self.make_timers()

        self.debug('pinkie.py started')
        self.debug('Listening on ports ' + ', '.join(self.listening))

    def die(self):
        for client in self.clients.values():
            client.die()

        self.async.die()


    def debug(self, msg):
        print('   ' + msg)
    def whine(self, msg):
        print('** ' + msg)

    def make_listeners(self):
        for port in self.cfg['bind_ports']:
            try:
                sock = socket.socket()
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind((self.cfg['bind_host'], port))
                self.listening.append(str(port))
                sock.listen(5)

                self.async.add_pollable(AsyncListen(sock, self.accept))
            except socket.error as e:
                self.whine("Failed to make listener on port {0}: {1}".format(port, e))

    def make_timers(self):
        self.async.add_timer(TimerRepeat(3, self.ping_tests))


    def numeric(self, client, num, message):
        client.numeric(self.si, num, message)

    def send_visible(self, who, source, message):
        for client in self.clients.values():
            for channel in client.channels:
                if channel in who.channels:
                    client.send(source, message)

    def snotice(self, message):
        for client in self.clients.values():
            if client.oper:
                client.notice(self.si, message)


    def on_error(self):
        e_type, e_value, e_traceback = sys.exc_info()

        err = traceback.format_exc()
        for line in err.split('\n'):
            if line != '':
                self.snotice(line)
        for line in err.split('\n'):
            if line != '':
                self.whine(line)

        if e_type == KeyboardInterrupt:
            self.die()

    def accept(self, conn, addr):
        client = IRCClient(self, conn)
        self.async.add_pollable(client)
        self.debug('Accepted connection from {0}'.format(addr))


    def nick_gen(self):
        self.guests += 1
        return 'guest-{0}'.format(self.guests)

    def nick_acceptable(self, client, nick):
        if nick.upper() in self.clients:
            self.numeric(client, '433', '{0} :Nickname is already in use'.format(nick))
            return False

        s = string.ascii_lowercase + string.ascii_uppercase + string.digits + '|\\[]{}`~^_-'

        for c in nick:
            if c not in s:
                self.numeric(client, '432', '{0} :Erroneous nickname'.format(nick))
                return False

        return True

    def nick_change(self, client, nick):
        if nick.upper() in self.clients:
            return

        self.send_visible(client, client.si, 'NICK {0}'.format(nick))
        for channel in client.channels:
            channel.nick_change(client, nick)

        del self.clients[client.si.cnick()]
        client.si.nick = nick
        self.clients[client.si.cnick()] = client


    def burst_client_list(self, client):
        for chan in self.channels.keys():
            line = self.channels[chan].list_line(client)

            if line != None:
                self.numeric(client, '322', line)

        self.numeric(client, '323', ':End of LIST')

    def burst_client_version(self, client):
        # hackish but readable way to do it
        global PINKIE

        s = [ ('001', ':Welcome to the {net} Internet Relay Chat Network {nick}'),
              ('004', ':{host} {version}'),
              ('005', ':CHANTYPES=# CHANMODES={cmode} PREFIX=(ov)@+ NETWORK={net} CASEMAPPING=ascii')]
        d = { 'net': self.cfg['net_name'],
              'nick': client.si.nick,
              'host': self.cfg['server_host'],
              'version': PINKIE['VERSION'],
              'cmode': IRCChannel.CHANNEL_MODES }

        for num, line in s:
            self.numeric(client, num, line.format(**d))

    def burst_client_motd(self, client):
        self.numeric(client, '375', ':- {0} Message of the day -'.format(self.cfg['server_host']))

        for line in self.cfg['motd']:
            self.numeric(client, '372', ':- {0}'.format(line))

        self.numeric(client, '376', ':End of MOTD command')

    def burst_client_connect(self, client):
        self.burst_client_version(client)
        self.burst_client_motd(client)

    def client_welcome(self, client):
        if client.si.cnick() in self.clients:
            self.whine('Assigning guest nick')
            client.si.nick = self.nick_generate()

        self.clients[client.si.cnick()] = client

        self.burst_client_connect(client)
        self.debug('Welcoming new client')
        self.snotice('New client connecting: {0}'.format(client.si))

        return True

    def client_quit(self, client, text):
        self.send_visible(client, client.si, 'QUIT :{0}'.format(text))
        client.raw('ERROR :Quit: {0}'.format(text))

        for chan in self.channels.values():
            chan.client_quit(client, text)

        self.debug('Dying client {0}'.format(client.si))
        client.do_send()
        client.die()

        self.prune_channels()
        self.prune_clients()


    def try_oper(self, client, opername, password):
        opers = self.cfg['opers']

        if opername in self.opers:
            return True

        if (not opername in opers) or (opers[opername] != password):
            self.numeric(client, '491', 'No oper blocks for your host')
            return False

        client.oper_up()
        self.numeric(client, '381', 'You are now an IRC operator')
        self.snotice('New operator {0} from {1}'.format(opername, client.si))

        return True


    def try_join(self, client, channel):
        uchan = channel.upper()

        if not uchan in self.channels:
            self.channels[uchan] = IRCChannel(self, channel, client)
        else:
            self.channels[uchan].client_join(client)

        client.channels.append(self.channels[uchan])

    def try_part(self, client, channel, text=None):
        uchan = channel.upper()
        if uchan in self.channels:
            self.channels[uchan].client_part(client, text)
            client.channels.remove(self.channels[uchan])

        self.prune_channels()


    def try_privmsg(self, client, dest, text):
        udest = dest.upper()
        if udest[0] == '#':
            if udest in self.channels:
                self.channels[udest].try_privmsg(client, text)
        else:
            if udest in self.clients:
                self.clients[udest].privmsg(client.si, text)

    def try_notice(self, client, dest, text):
        udest = dest.upper()
        if udest[0] == '#':
            if udest in self.channels:
                self.channels[udest].try_notice(client, text)
        else:
            if udest in self.clients:
                self.clients[udest].notice(client.si, text)


    def try_mode(self, client, channel, args):
        uchan = channel.upper()

        if not uchan in self.channels:
            self.numeric(client, '403', '{0} :No such channel'.format(channel))
            return

        if len(args) == 0:
            self.channels[uchan].send_mode(client)
        else:
            self.channels[uchan].try_mode(client, args[0], args[1:])


    def try_topic(self, client, channel, topic):
        uchan = channel.upper()

        if not uchan in self.channels:
            self.numeric(client, '403', '{0} :No such channel'.format(channel))
            return

        self.channels[uchan].try_topic(client, topic)

    def send_topic(self, client, channel, topic):
        uchan = channel.upper()

        if not chan in self.channels:
            self.numeric(client, '403', '{0} :No such channel'.format(channel))
            return

        self.channels[uchan].burst_client_topic(client)

    
    def prune_channels(self):
        for chan in list(self.channels.keys()):
            if self.channels[chan].is_empty():
                del self.channels[chan]

    def prune_clients(self):
        for cli in list(self.clients.keys()):
            if not self.clients[cli].alive():
                del self.clients[cli]

    def ping_tests(self, timer):
        for client in self.clients.values():
            client.ping_test()
        self.prune_clients()


    def run(self):
        self.async.loop()


if __name__ == '__main__':
    cfg = {'motd': ['failed to find pinkie.conf']}

    try:
        f = open('pinkie.conf', 'r')
        if f:
            cfg = json.load(f)
            f.close()
    except IOError:
        print('Error: could not open configuration file pinkie.conf')

    ircd = IRCd(cfg)
    ircd.run()
