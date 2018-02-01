import socket

class Redis(object):
    def __init__(self, host, port):
        self.conn = socket.socket()
        self.conn.connect((host, port))

    def _send_request(self, args):
        self.conn.send('*%d\r\n' % len(args))
        for arg in args:
            if isinstance(arg, unicode):
                arg = arg.encode('utf-8')
            else:
                arg = str(arg)
            self.conn.send('$%d\r\n%s\r\n' % (len(arg), arg))

    def _parse_reply(self, expected='+*$:'):
        prefix = self.conn.recv(1)
        line = ''
        while not line.endswith('\r\n'):
            ch = self.conn.recv(1)
            if ch == '': raise EOFError()
            line += ch
        line = line[:-2]
        if prefix == '-':
            raise RuntimeError('redis error: %s' % line)
        elif prefix not in expected:
            raise RuntimeError('unexpected response: %s%s' % (prefix, line))
        elif prefix == '+':
            return line
        elif prefix == ':':
            return int(line)
        elif prefix == '$':
            slen = int(line)
            if slen == -1: return None # distinguished from empty bulk reply
            line = self.conn.recv(slen)
            trail = self.conn.recv(2)
            assert len(line) == slen and trail == '\r\n'
            return line
        elif prefix == '*':
            results = []
            blen = int(line)
            if blen == -1: return None # distinguished from empty multi-bulk reply
            for i in xrange(blen):
                results.append(self._parse_reply('+$:'))
            return results
        else:
            return (prefix, line)

    def __getattr__(self, name):
        def inner(*args):
            self._send_request((name,) + args)
            return self._parse_reply()
        return inner

if __name__ == '__main__':
    r = Redis('127.0.0.1', 6379)
    r.select(1)
    print r.keys('*')
    r.quit()