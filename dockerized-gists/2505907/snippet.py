from gevent.server import StreamServer
#import gevent
import time

class ClientDisconnected(Exception):
    pass

class Handler(object):
    def __init__(self, cache, socket, address):
        self.cache = cache
        self.socket = socket
        self.address = address
        self.sockfile = self.socket.makefile()

    def send(self, data):
        self.sockfile.write(data + '\r\n')
        self.sockfile.flush()

    def send_error(self):
        self.send('ERROR')

    def send_client_error(self, error):
        self.send('CLIENT_ERROR ' + error)

    def send_server_error(self, error):
        self.send('SERVER_ERROR ' + error)
        self.sockfile.close()

    def recv(self):
        data = self.sockfile.readline()
        if data == '':
            raise ClientDisconnected()
        return data.rstrip()

    def handle(self):
        while True:
            try:
                command = self.recv()
            except ClientDisconnected:
                return
            parts = command.split()
            if not parts:
                import ipdb; ipdb.set_trace()
                continue
            command = parts[0].lower()
            if command in ('get', 'gets'):
                if len(parts) != 2:
                    self.send_client_error('Invalid number of arguments (1 expected)')
                    continue
                keys = parts[1:]
                if not all(is_valid_key(key) for key in keys):
                    self.send_client_error('Invalid key')
                    continue
                for key in keys:
                    ret = self.cache.get(key)
                    if ret:
                        value = ret[0]
                        flags = ret[2]
                        reply = 'VALUE ' + key + ' ' + str(flags) + ' ' + str(len(value))
                        if ret[3]:
                            reply += ' ' + str(ret[3])
                        reply += '\r\n' + value
                        self.send(reply)
                self.send('END')
            elif command in ('cas', 'set', 'add', 'replace', 'append', 'prepend'):
                expected_length = (6 if command is 'cas' else 5)
                noreply = parts[-1].lower() == 'noreply'
                if noreply:
                    expected_length += 1
                if len(parts) != expected_length:
                    self.send_client_error('Invalid number of arguments (%d expected)' % (expected_length - 1))
                    continue
                key = parts[1]
                flags = int(parts[2])
                expire = normalize_expire(int(parts[3]))
                length = int(parts[4])
                cas = int(parts[5]) if command == 'cas' else None
                value = self.sockfile.read(length+2)[:-2]
                if not is_valid_key(key):
                    self.send_client_error('Invalid key')
                    continue

                command_runner = getattr(self.cache, command)
                args = [key, value, expire, flags]
                if cas:
                    args.append(cas)
                reply = command_runner(*args)

                if not noreply:
                    self.send(reply)
            elif command == 'delete':
                if len(parts) == 1:
                    self.send_client_error('Invalid number of arguments (1 expected)' )
                    continue

                key = parts[1]
                if not is_valid_key(key):
                    self.send_client_error('Invalid key')
                    continue

                delete_time = normalize_expire(parts[2]) if len(parts) > 2 else None

                noreply = parts[-1].lower() == 'noreply'

                reply = self.cache.delete(key, delete_time)
                if not noreply:
                    self.send(reply)

            elif command in ('incr', 'decr'):
                if len(parts) < 3:
                    self.send_client_error('Invalid number of arguments (2 expected)' )
                    continue

                key = parts[1]
                if not is_valid_key(key):
                    self.send_client_error('Invalid key')
                    continue

                value = int(parts[2])
                if command == 'incr':
                    reply = self.cache.incr(key, value)
                else:
                    reply = self.cache.decr(key, value)

                noreply = parts[-1].lower() == 'noreply'
                if not noreply:
                    self.send(reply)

            elif command == 'stats':
                self.send_server_error('Stats not implemented')
            else:
                self.send_error()

def is_valid_key(key):
    if len(key) < 250:
        return True

def normalize_expire(expire):
    if expire == 0:
        return None
    if expire <= 2592000: # 60*60*24*30, 30 days
        expire = expire + time.time()
    return expire

class Cache(object):
    def __init__(self):
        self.cache = {}

    def set(self, key, value, expire=None, flags=None):
        self.cache[key] = (value, expire, flags, None)
        return 'STORED'

    def add(self, key, value, expire=None, flags=None):
        entry = self.get(key)
        if not entry:
            self.cache[key] = (value, expire, flags, None)
            return 'STORED'
        return 'NOT_STORED'

    def replace(self, key, value, expire=None, flags=None):
        entry = self.get(key)
        if entry:
            self.cache[key] = (value, expire, flags, None)
            return 'STORED'
        return 'NOT_STORED'

    def append(self, key, value, expire=None, flags=None):
        entry = self.get(key)
        if entry:
            new_value = entry[0] + value
            self.cache[key] = (new_value, expire, flags, None)
            return 'STORED'
        return 'NOT_STORED'

    def prepend(self, key, value, expire=None, flags=None):
        entry = self.get(key)
        if entry:
            new_value = value + entry[0]
            self.cache[key] = (new_value, expire, flags, None)
            return 'STORED'
        return 'NOT_STORED'

    def cas(self, key, value, expire=None, flags=None, cas=None):
        entry = self.get(key)
        if entry:
            if entry[3] == cas:
                self.cache[key] = (value, expire, flags, cas)
                return 'STORED'
            else:
                return 'EXISTS'
        return 'NOT_FOUND'

    def get(self, key):
        try:
            value, expire, flags, cas = self.cache[key]
        except KeyError:
            return None
        else:
            if expire is not None and expire < time.time():
                self.delete(key)
                return None
            return value, expire, flags, cas

    def delete(self, key, time):
        # TODO: handle time properly (disallow add/replace) and delay deletion
        try:
            del self.cache[key]
        except KeyError:
            return 'NOT_FOUND'
        return 'DELETED'

    def incr(self, key, value):
        entry = self.get(key)
        if entry:
            new_value = str(int(entry[0]) + value)
            self.cache[key] = (new_value, entry[1], entry[2], entry[3])
            return new_value
        return 'NOT_FOUND'

    def decr(self, key, value):
        entry = self.get(key)
        if entry:
            new_value = str(int(entry[0]) - value)
            self.cache[key] = (new_value, entry[1], entry[2], entry[3])
            return new_value
        return 'NOT_FOUND'

    def handle_client(self, socket, address):
        handler = Handler(self, socket, address)
        handler.handle()

cache = Cache()
server = StreamServer(('127.0.0.1', 11211), cache.handle_client)

server.start()
server.serve_forever()
