# -*- coding: utf-8 -*-
"""
    Based on:
        https://gist.github.com/meeuw/c3bc9dd07945c87c89e6#file-findfiles-py
        https://bitbucket.org/nosklo/pysmbclient/wiki/Home
"""

import os
import pexpect
import re
import locale
import datetime
import time
import logging

__logger__ = logging.getLogger(os.path.basename(__file__))

try:
    datetime_strptime = datetime.datetime.strptime
except AttributeError:
    # python version older than 2.5
    def datetime_strptime(date, format):
        return datetime.datetime(*(time.strptime(date, format)[:6]))

_volume_re = re.compile(r"""
Volume:\s        # label
\|([^|]*)\|\s     # the volume name
serial\snumber\s # another label
0x([a-f0-9]+)    # hex serial number
$                # end of line
""", re.VERBOSE)

_smb_header_re = re.compile(r"""
Domain=\[([^]]+)\]\s
OS=\[([^]]+)\]\s
Server=\[([^]]+)\]
$
""", re.VERBOSE)


_file_re = re.compile(r"""
\s*               # file lines start with some spaces
(.*?)\s+            # capture filename non-greedy, eating remaining spaces
([ADHSR]*)          # capture file mode
\s+                 # after the mode you can have any number of spaces
(\d+)               # file size
\s+                 # spaces after file size
(                   # begin date capturing
    \w{3}               # abbrev weekday
    \s                  # space
    \w{3}               # abbrev month
    \s{1,2}             # one or two spaces before the day
    \d{1,2}             # day
    \s                  # a space before the time
    \d{2}:\d{2}:\d{2}   # time
    \s                  # space
    \d{4}               # year
)                   # end date capturing
$                   # end of string""", re.VERBOSE)

_cwd_re = re.compile(ur"Current directory is \\\\(?P<host>[^\\]+)\\((?P<share>[^\\]+))(?P<rel_path>.+)")

_SMB_PROMPT = ur'smb:\s.*\>'

def _to_smb_path_fmt(path):
    return path.replace(os.sep, '\\')

def _to_local_path_fmt(path):
    return path.replace('\\', os.sep)

class SambaClientError(OSError): pass

class SambaClient():
    def __init__(self, host, share, username, domain=".", password=""):
        smb_cmd = 'smbclient -W {domain} -U "{username}" //{host}/{share}/'.format(**locals())
        self.username = username
        self.domain = domain
        self.host = host
        self.share = share
        self.p = pexpect.spawn(smb_cmd, )
        self._put_pwd(password)
        self._runcmd_error_on_data("prompt ON")

    def _put_pwd(self, pwd):
        self.p.expect(ur'(?i).*password:')
        self.p.sendline(pwd)
        self.p.expect(_SMB_PROMPT)

    def _runcmd(self, command=None, *args):
        if command:
            f_args = " ".join('"%s"' % arg for arg in args)
            full_cmd = command  + " " + f_args
            __logger__.debug("SMBCLIENT CMD: {0}".format(full_cmd))
            self.p.sendline(full_cmd)
        self.p.expect(_SMB_PROMPT)
        raw_out = self.p.before.decode('utf-8')
        return raw_out.replace(full_cmd, "", 1).strip()

    def _runcmd_error_on_data(self, cmd, *args):
        """raises SambaClientError if cmd returns any data"""
        def term_bs_in_out(s):
            return " \b" in s
        data = self._runcmd(cmd, *args)
        if data and not term_bs_in_out(data):
            raise SambaClientError("Error on %r: %r" % (cmd, data))
        return data

    def lsdir(self, path):
        """
        Lists a directory
        returns a list of tuples in the format:
        [(filename, modes, size, date), ...]
        """
        path = os.path.join(path, u'*')
        return self.glob(path)

    def glob(self, path):
        """
        Lists a glob (example: "/files/somefile.*")
        returns a list of tuples in the format:
        [(filename, modes, size, date), ...]
        """
        files = self._runcmd(u'ls', path).splitlines()
        for filedata in files:
            m = _file_re.match(filedata)
            if m:
                name, modes, size, date = m.groups()
                if name == '.' or name == '..':
                    continue
                size = int(size)
                # Resets locale to "C" to parse english date properly
                # (non thread-safe code)
                loc = locale.getlocale(locale.LC_TIME)
                locale.setlocale(locale.LC_TIME, 'C')
                date = datetime_strptime(date, '%a %b %d %H:%M:%S %Y')
                locale.setlocale(locale.LC_TIME, loc)
                yield (name, modes, size, date)

    def listdir(self, path):
        """Emulates os.listdir()"""
        result = [f[0] for f in self.lsdir(path)]
        if not result: # can mean both that the dir is empty or not found
            # disambiguation: verifies if the path doesn't exist. Let the error
            # raised by _getfile propagate in that case.
            self._getfile(path)
        return result

    def _getfile(self, path):
        try:
            f = self.glob(path).next()
        except StopIteration:
            raise SambaClientError('Path not found: %r' % path)
        return f

    def info(self, path):
        """Fetches information about a file"""
        path = _to_smb_path_fmt(path)
        data = self._runcmd(u'allinfo', path)
        if data.startswith('ERRSRV'):
            raise SambaClientError(
                'Error retrieving info for %r: %r' % (path, data.strip()))
        result = {}
        for info in data.splitlines():
            k, sep, v = info.partition(':')
            if sep:
                result[k.strip()] = v.strip()
        return result

    def diskinfo(self):
        """Fetches information about a volume"""
        data = self._runcmd('volume')
        for line in data.splitlines():
            m = _volume_re.match(line)
            if m:
                name, serial = m.groups()
                return name, int(serial, 16)
        else:
            raise SambaClientError(
                'Error retrieving disk information: %r' % data)

    def volume(self):
        """Fetches the volume name"""
        return self.diskinfo()[0]

    def serial(self):
        """Fetches the volume serial"""
        return self.diskinfo()[1]

    def isdir(self, path):
        """Returns True if path is a directory/folder"""
        return 'D' in self._getfile(path)[1]

    def isfile(self, path):
        """Returns True if path is a regular file"""
        return not self.isdir(path)

    def exists(self, path):
        """Returns True if path exists in the remote host"""
        try:
            self._getfile(path)
        except SambaClientError:
            return False
        else:
            return True

    def mkdir(self, path):
        """Creates a new folder remotely"""
        path = _to_smb_path_fmt(path)
        self._runcmd_error_on_data(u'mkdir', path)

    def cd(self, path):
        """Change remote dir"""
        path = _to_smb_path_fmt(path)
        self._runcmd_error_on_data(u'cd', path)

    def lcd(self, path):
        """Change local dir"""
        self._runcmd_error_on_data(u'lcd', path)

    def rmdir(self, path):
        """Removes a remote empty folder"""
        path = _to_smb_path_fmt(path)
        self._runcmd_error_on_data(u'rmdir', path)

    def unlink(self, path):
        """Removes/deletes/unlinks a file or folder"""
        path = _to_smb_path_fmt(path)
        if self.isdir(path):
            try:
                self.set_recurse()
                self._runcmd_error_on_data(u'del', path + "\\*")
                self.rmdir(path)
            finally:
                self.set_recurse(False)
        else:
            self._runcmd_error_on_data(u'del', path)

    remove = unlink

    def chmod(self, path, *modes):
        """Set/reset file modes
        Tested with: AHS

        smbc.chmod('/file.txt', '+H')
        """
        path = _to_smb_path_fmt(path)
        plus_modes = []
        minus_modes = []
        for mode in modes:
            if mode.startswith(u'-'):
                minus_modes.append(mode.lstrip(u'-'))
            else:
                plus_modes.append(mode.lstrip(u'+'))
        modes = []
        if plus_modes:
            modes.append(u'+%s' % u''.join(plus_modes))
        if minus_modes:
            modes.append(u'-%s' % u''.join(minus_modes))
        self._runcmd_error_on_data(u'setmode', u''.join(modes))

    def rename(self, old_name, new_name):
        old_name = _to_smb_path_fmt(old_name)
        new_name = _to_smb_path_fmt(new_name)
        self._runcmd_error_on_data(u'rename', old_name, new_name)

    def download_file(self, remote_path, local_path):
        remote_path = _to_smb_path_fmt(remote_path)
        result = self._runcmd(u'get', remote_path, local_path)

    def upload_file(self, local_path, remote_path):
        remote_path = _to_smb_path_fmt(remote_path)
        result = self._runcmd(u'put', local_path, remote_path)

    def upload_update(self, local_path, remote_path):
        remote_path = _to_smb_path_fmt(remote_path)
        result = self._runcmd(u'reput', local_path, remote_path)

    def walk(self, top, topdown=True):
        names = self.glob(os.path.join(top, "*"))

        dirs, nondirs = [], []
        for item in names:
            if 'D' in item[1]:
                dirs.append(item[0])
            else:
                nondirs.append(item[0])
        if topdown:
            yield top, dirs, nondirs
        for name in dirs:
            new_path = os.path.join(top, name)
            for x in self.walk(new_path, topdown):
                yield x
        if not topdown:
            yield top, dirs, nondirs

    def upload(self, local_path, remote_path):
        if os.path.isdir(local_path):
            if not self.exists(remote_path):
                self.makedirs(remote_path)
            for root, dirs, files in os.walk(local_path):
                remote_root = root.replace(local_path, _to_local_path_fmt(remote_path))
                for d in dirs:
                    rem_dir = _to_smb_path_fmt(os.path.join(remote_root, d))
                    if not self.exists(rem_dir):
                        self.makedirs(rem_dir)
                for f in files:
                    rem_f = _to_smb_path_fmt(os.path.join(remote_root, f))
                    self.upload_file(os.path.join(root, f), rem_f)
        else:
            basedir = os.path.dirname(remote_path)
            if not self.exists(basedir):
                self.makedirs(basedir)
            self.upload_file(local_path, remote_path)

    def download(self, remote_path, local_path):
        if self.isdir(remote_path):
            if not os.path.exists(local_path):
                os.makedirs(local_path)
            for root, dirs, files in self.walk(remote_path):
                local_root = root.replace(_to_local_path_fmt(remote_path), local_path)
                for d in dirs:
                    loc_dir = os.path.join(local_root, d)
                    if not os.path.exists(loc_dir):
                        os.makedirs(loc_dir)
                for f in files:
                    loc_f = os.path.join(local_root, f)
                    self.download_file(_to_smb_path_fmt(os.path.join(root, f)), loc_f)
        else:
            basedir = os.path.dirname(local_path)
            if not os.path.exists(basedir):
                self.makedirs(basedir)
            self.download_file(remote_path, local_path)

    def get_cwd(self):
        out = self._runcmd(u'pwd').strip()
        m = _cwd_re.search(out)
        if m:
            return m.groupdict()["rel_path"]
        else:
            raise SambaClientError("pwd command fail")

    def makedirs(self, remote_path):
        remote_path = _to_smb_path_fmt(remote_path)
        dir_items = remote_path.split("\\")
        for i in xrange(len(dir_items)):
            part_path = "\\".join(dir_items[:i+1])
            if not self.exists(part_path):
                self.mkdir(part_path)

    def set_recurse(self, recurse=True):
        cwd = self.get_cwd()
        try:
            if cwd != "\\": self.cd("\\")
            flag = "ON" if recurse else "OFF"
            self._runcmd_error_on_data("recurse {0}".format(flag))
        finally:
            if cwd != "\\": self.cd(cwd)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()

    def __repr__(self):
        return '<SambaClient({self.domain}\\{self.username}@//{self.host}/{self.share})>'.format(self=self)

    def close(self):
        pass

