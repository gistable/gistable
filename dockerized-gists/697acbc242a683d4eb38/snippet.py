# Paramiko SSH Object with batch commands and stdin
# Blake VandeMerwe July 2014
#
# Adapted from Joe Linoff's code at http://joelinoff.com/blog/?p=905
# his did not work for me, so I fixed it and added some features.
#
import re
import string
import logging
import socket
import time
import datetime

try:
    import paramiko
except ImportError, e:
    raise ImportError('paramiko module required: pip install -U paramiko')

class Batch(object):
    def __init__(self, *commands):
        commands = list(commands)
        self.commands = list()
        self.add(commands)

    def __str__(self): return ' && '.join(self.commands)
    def __add__(self, other): return self.add(other.commands)
    def __radd__(self, other): return other.add(self.commands)

    def add(self, commands):
        if not hasattr(commands, '__iter__'):
            self.commands.append(str(commands.strip()))
        else: 
            for command in commands:
                command = command.strip()
                self.commands.append(command)
        return self

class SSH:
    re_newlines = re.compile(r'[\n|\r]', re.UNICODE + re.I + re.M)
    re_color_codes = re.compile(r'(\[0m)|(\[0\d\;\d{2}m)', re.UNICODE)

    def __init__(self, 
            connection_object, 
            host_key_policy = paramiko.AutoAddPolicy, 
            key_filename = None, 
            compress = True, 
            verbose = False):

        for req_key in ['username', 'ip_address']:
            if req_key not in connection_object.keys():
                raise RuntimeWarning('connection_object did not contain the required key {0}'.format(req_key))

        self.clear()
        self.connection_object = dict(connection_object)

        if key_filename is not None:
            self.connection_object.setdefault('key_filename', key_filename)

        self.ssh = None
        self.transport = None
        self.compress = compress
        self.host_key_policy = host_key_policy
        self.buffer_size = 1024 * 64 # bytes

        self.logger = logging.getLogger('SSH')

        logging_format = '%(asctime)s {0}: %(message)s'.format(self)
        format = logging.Formatter(logging_format)
        handler = logging.StreamHandler()
        handler.setFormatter(format)
        self.logger.addHandler(handler)
        self.info = self.logger.info
        self.err = self.logger.warning

        self.set_verbosity(verbose)
        self.info('Initialized SSH object')

    def __del__(self):
        self.__disconnect()

    def __str__(self):
        status, output = self.last
        return '<SSH-{0}@{1}> {2}'.format(
            self.connection_object['username'], 
            self.connection_object['ip_address'],
            ('\n==== stdout: \n' + ' '.join(output)) if output else '')

    @property
    def connected(self):
        return self.transport is not None

    @property
    def last(self):
        try:
            return self.results[-1]
        except IndexError, e:
            return -1, ''

    @property
    def last_line(self):
        try:
            status, output = self.last
            return output[-1]
        except IndexError, e:
            return ''

    @property
    def last_command(self):
        try:
            return self._history[-1]
        except IndexError, e:
            return ''

    @property
    def history(self):
        return self._history

    @property
    def verbose(self):
        return self._verbose

    @property
    def disconnected(self):
        return not self.connected

    def close(self):
        self.__disconnect()

    def disconnect(self):
        self.__disconnect()

    def clear(self, history = True, results = True):
        if history: 
            self._history = list()
        if results: 
            self.results = list()
        return self

    def set_verbosity(self, verbosity_level = logging.ERROR):
        self.info('Changing verbosity from {0} to {1}'.format(
            self.logger.level, int(verbosity_level)))

        self._verbose = int(verbosity_level)
        if not verbosity_level:
            self.logger.setLevel(logging.INFO)
        else: 
            self.logger.setLevel(verbosity_level)

    def __connect(self):
        self.info('Connecting')

        ip = self.connection_object['ip_address']
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(self.host_key_policy())
        try:
            ssh.connect( hostname = ip,
                         username = self.connection_object['username'],
                         password = self.connection_object.get('password', None),
                         key_filename = self.connection_object.get('key_filename', None),
                         port = self.connection_object.get('port', 22))

            self.transport = ssh.get_transport()
            self.transport.use_compression(self.compress)
            self.ssh = ssh
            self.info('Connected')

        except socket.error as e:
            self.transport = None
            self.err('Could not connect with error: {0}'.format(str(e)))

        except paramiko.BadAuthenticationType as e:
            self.transport = None
            self.err('AuthenticationError: {0}'.format(str(e)))

        return self.transport is not None

    def __disconnect(self):
        self.info('Disconnected')
        if self.transport is not None:
            self.transport.close()
            self.transport = None

    def __clean_input_data(self, inpt):
        self.info('Sanitizing input data')

        if inpt is None: return []
        if '\\n' in inpt:
            lines = inpt.split('\\n')
            inpt = '\n'.join(lines)

        ret = inpt.split('\n')
        return ret

    def __clean_output_data(self, output):
        output = output.strip()
        output = self.re_newlines.sub(' ', output)
        output = output.split(' ')

        out = [x.strip() for x in output if x not in ['', '\r', '\r\n', '\n\r', '\n']]
        ret = list()

        for line in out:
            new_line = filter(lambda x: x in string.printable, line)
            new_line = self.re_color_codes.sub('', new_line)
            ret.append(new_line)
        return ret


    def __run_polling(self, session, timeout, inpt):
        indx = 0
        interval = 0.1
        timeout_flag = False
        start = datetime.datetime.now()
        output = ''

        session.setblocking(0)
        while True:
            if session.exit_status_ready():
                break

            if session.recv_ready():
                output += str(session.recv(self.buffer_size))

                if session.send_ready():
                    snd = inpt[indx] if indx < len(inpt) else ''

                    session.send(snd + '\n')
                    indx = indx + 1

            now = datetime.datetime.now()
            elapsed = (now - start).total_seconds()

            if elapsed > timeout:
                timeout_flag = True
                break
            time.sleep(interval)

        if session.recv_ready():
            output += str(session.recv(self.buffer_size))
        if timeout_flag:
            self.info('Request timed out after {0}s'.format(timeout))
            session.close()
        return output


    def execute(self, command, inpt = None, timeout = None, verbose = None):
        original_verbosity = self.verbose       # grab the original verbosity if we change for execute()

        if verbose is not None: 
            self.set_verbosity(verbose)         # set the temporary verbosity if supplied

        self.info('Executing command: {0}, stdin={1}'.format(command, str(inpt)))

        if timeout is None:                     # if no timeout is supplied, look in connection_obj, else 5s
            timeout = self.connection_object.get('timeout', 5)

        if self.transport is None:              # attempt to connect
            if not self.__connect():
                self.err('No connection. Closing')

                return self

        if isinstance(command, list):           # ['cd', 'ls'] => Batch('cd', 'ls')
            command = Batch(*command)

        if isinstance(command, Batch):          # Batch('cd', 'ls') => 'cd && ls'
            command = str(command)

        inpt = self.__clean_input_data(inpt)    # handle newlines
        session = self.transport.open_session() # open a new session using underlying transport
        session.set_combine_stderr(True)        # combine STDOUT and STDERR
        session.get_pty()                       # get the remote terminal dimensions
        session.exec_command(command)           # execute our command; 'cd && ls'
        stdin = session.makefile('wb', -1)      # temp stdin from transport
        stdout = session.makefile('rb', -1)     # temp stdout from transport
                                                # poll the session, inserting input when asked; timeout in seconds
        original_output = self.__run_polling(session, timeout, inpt)
                                                # original_output will contain a value when polling is done; clean it
        output = self.__clean_output_data(original_output)
        status = session.recv_exit_status()     # get the exit status; 0 for success

        if self.verbose:
            self.info('Captured stdout, original {0} bytes -- reduced to {1} bytes'.format(
                len(original_output), len(' '.join(output))))

        res = (status, output,)                 # return tuple of exit status and cleaned output
        self._history.append((command, inpt,))  # append the command to our ssh history
        self.results.append(res)                # append the stdout
        self.set_verbosity(original_verbosity)  # reset the verbosity
        return self                             # return self for chaining


# usage
# ========================
ssh = SSH({
    'ip_address': '127.0.0.1', 
    'username': 'Blake', 
    'password': 'password123'}, verbose = True)

a = Batch('cd ~', 'ls', 'echo "hello"')
ssh.execute(a)

b = a + Batch('cd ~/.ssh', 'echo "world"')
ssh.execute(b)

ssh.execute('sudo echo "Administrator Task"', inpt = '<password>')

print ssh.last
print ssh.history
print ssh.results