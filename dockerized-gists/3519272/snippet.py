from telnetlib import Telnet

class RedisLiteClient:
  """
  Super lightweight no-frills blocking Redis client that doesn't require any additional dependencies.

  This is a microlibrary, designed for easy copy'n'paste into a project, where you don't want to
  rely on pip/easy_install/etc.

  Usage:
    redis = RedisLiteClient(host='...', [db=4])
    redis.execute('SET', 'somekey', 'foo')    # returns True
    redis.execute('GET', 'somekey')           # returns 'foo'
    redis.execute('GET', 'anotherkey')        # returns None
    redis.execute('SET', 'anotherkey', 'foo') # returns True
    redis.execute('KEYS', '*')                # returns ['somekey', 'anotherkey']
    redis.execute('YOURMOMMA')                # raises exception
    redis.close()

  -Joe Walnes
  """

  def __init__(self, host='localhost', port=6379, db=0, timeout=10, debug=False):
    self._connection = Telnet(host, port, timeout)
    self._timeout = timeout
    self._debug = debug
    if db:
      if self.execute('SELECT', db) != 'OK':
        raise RuntimeError('Could not select db %d' % db)

  def execute(self, *request):
    # Send
    if self._debug:
      print 'Redis Request: %s' % json.dumps(request)
    self._sendline('*%d' % len(request))
    for arg in request:
      as_string = str(arg)
      self._sendline('$%d' % len(as_string))
      self._sendline(as_string)

    # Process response
    def read_command():
      line = self._readline()
      prefix = line[0]
      rest = line[1:]
      if prefix == '+':
        return rest
      elif prefix == '-':
        raise RuntimeError('Redis error: %s' % rest)
      elif prefix == ':':
        return int(rest)
      elif prefix == '$':
        data_length = int(rest)
        if data_length == -1:
          return None
        else:
          data = ''
          first = True
          while len(data) < data_length:
            if not first:
              data += '\r\n'
            data += self._readline()
            first = False
          return data
      elif prefix == '*':
        # Recurse
        return list([read_command() for c in range(int(rest))])
      else:
        raise RuntimeError('Unknown response prefix "%s"' % prefix)

    response = read_command()
    if self._debug:
      print 'Redis Response: %s' % json.dumps(response)
    return response

  def close(self):
    self._connection.close()

  def _sendline(self, line):
    if self._debug:
      print 'Redis write: "%s"' % line
    self._connection.write(line)
    self._connection.write('\r\n')

  def _readline(self):
    line = self._connection.read_until('\r\n', self._timeout)[:-2]
    if self._debug:
      print 'Redis read : "%s"' % line
    return line
