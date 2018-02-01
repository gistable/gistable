import time
import socket
import paramiko
import socks

SOCKS5_HOST = "nnn.nnn.nnn.nnn"
SOCKS5_PORT = 12345

SERVER_IP = "nnn.nnn.nnn.nnn"
SERVER_PORT = 54321
SERVER_ENCODING = "utf-8"

USER_ID = "userid"
USER_PASS = "userpassword"

SUCCESS_TOKEN = "successfully"


def read_until(chan, s):
    temp = ""
    cnt = 0
    while cnt < 10:
        try:
            temp = temp + chan.recv(1200)
            if temp.find(s) >= 0:
                break
        except socket.timeout:
            cnt += 1
            time.sleep(0.5)

    if cnt >= 10:
        raise socket.timeout(unicode(temp, SERVER_ENCODING))

    return temp


class Result:
    def __init__(self):
        self.log = ''
        self.success = False

    def add_log(self, s):
        self.log += s


class SSH(object):
    def __init__(self, host, port, server_encoding):
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, host, port, False)
        paramiko.client.socket.socket = socks.socksocket
        self.SERVER_ENCODING = server_encoding

    def create_connection(self, host, port, username, password):
        self._ssh = paramiko.SSHClient()
        self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._ssh.connect(hostname=host, port=port, username=username, password=password)
        self.chan = self._ssh.invoke_shell()
        self.chan.settimeout(0)

    # little example to do something with open connection
    def change_password(self, oldpass, newpass):
        result = Result()

        s = read_until(self.chan, 'login: ')
        result.add_log(self._u(s))
        self.chan.send('passwd\n')

        s = read_until(self.chan, ':')
        result.add_log(self._u(s))
        self.chan.send('%s\n' % oldpass)

        s = read_until(self.chan, ':')
        result.add_log(self._u(s))
        self.chan.send('%s\n' % newpass)

        s = read_until(self.chan, ':')
        result.add_log(self._u(s))
        self.chan.send('%s\n' % newpass)

        s = read_until(self.chan, '.')
        ss = self._u(s)
        result.add_log(ss)
        if ss.find(self._u(SUCCESS_TOKEN)) >= 0:
            result.success = True
        else:
            result.success = False
        return result

    def _u(self, s):
        return unicode(s, self.SERVER_ENCODING)

    def close(self):
        self._ssh.close()


if __name__ == "__main__":
    sshch = SSH(SOCKS5_HOST, SOCKS5_PORT, SERVER_ENCODING)
    sshch.create_connection(SERVER_IP, SERVER_PORT,
                            username=USER_ID, password=USER_PASS)
    new_pass = raw_input("New password: ")
    result = sshch.change_password(USER_PASS, new_pass)
    sshch.close()
    if not result.success:
        print result.log
        raise SystemExit("Error: Changing password failed")
    else:
        print "Password changed successfully"