from copy import copy
import os
import sys
from twisted.cred import error, portal
from twisted.cred.checkers import ICredentialsChecker
from twisted.cred.credentials import IUsernameHashedPassword, IUsernamePassword
from twisted.conch import avatar
from twisted.conch.checkers import SSHPublicKeyDatabase
from twisted.conch.ssh import connection, factory, keys, session, userauth
from twisted.internet import defer, protocol, reactor
from twisted.python import components, failure, log
from zope.interface import implements
import win32security


"""
Server for accepting incoming Jenkins connections via SSH on Windows.
Only supports running commands - won't give you a usable terminal.

Assumes that C:\Users\me\.ssh contains an RSA keypair for use as the host SSH keys
and a public key associated with a private key on the Jenkins master (which will connect as user 'jenkins').

Runs commands using Git Bash sh.exe, which makes it easier for Jenkins to connect and execute commands.
Assumes this is available in Program Files\Git\bin.

I use this to run Jenkins jobs on Windows hosts where the jobs need to run in a windows logon session (has a GUI).
I start this server using a logon task and have the machines set to logon on boot.

Listens on port 5022.

Copyright 2014 Box, Inc. All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


log.startLogging(sys.stderr)


class WindowsSshAvatar(avatar.ConchUser):
    """Represents the user accessing the ssh server."""
    def __init__(self, username):
        avatar.ConchUser.__init__(self)
        self.usernmae = username
        self.channelLookup.update({'session': session.SSHSession})
        self.listeners = {}

    def logout(self):
        """Stop listening on all connections"""
        for listener in self.listeners.itervalues():
            listener.stopListening()


class WindowsSshRealm(object):
    implements(portal.IRealm)

    def __init__(self):
        super(WindowsSshRealm, self).__init__()

    def requestAvatar(self, username, mind, *interfaces):
        user = WindowsSshAvatar(username)
        return interfaces[0], user, user.logout


class WindowsSshSession(object):
    def __init__(self, avatar):
        super(WindowsSshSession, self).__init__()
        self.avatar = avatar
        self.environ = copy(os.environ)

    def getPty(self, term, windowSize, attrs):
        self.environ['TERM'] = term
        self.winSize = windowSize
        self.attrs = attrs

    def execCommand(self, protocol, cmd):
        """Executes the command specified by cmd."""
        from twisted.internet import reactor
        program_files = 'C:\\Program Files{}\\'.format(' (x86)' if sys.maxsize > 2**32 else '')
        shell = program_files + 'Git\\bin\\sh.exe'
        command = (shell, '-c', cmd)
        peer = self.avatar.conn.transport.transport.getPeer()
        host = self.avatar.conn.transport.transport.getHost()
        self.environ['SSH_CLIENT'] = '{} {} {}'.format(peer.host, peer.port, host.port)
        self.pty = reactor.spawnProcess(protocol, shell, command, self.environ)
        self.avatar.conn.transport.transport.setTcpNoDelay(1)

    def openShell(self, transport):
        log('No interactive shell')

    def eofReceived(self):
        pass

    def closed(self):
        pass


components.registerAdapter(WindowsSshSession, WindowsSshAvatar, session.ISession)


# Read host SSH keys for use as the server.
with open('C:\\Users\\me\\.ssh\\host_rsa.pub') as public_key_file:
    public_key = public_key_file.read()
with open('C:\\Users\\me\\.ssh\\host_rsa') as private_key_file:
    private_key = private_key_file.read()
# Read public key file associated with a private key on the Jenkins master
with open('C:\\Users\me\\.ssh\\jenkins_rsa.pub') as jenkins_public_key_file:
    jenkins_public_key = jenkins_public_key_file.read()


class WindowsSshFactory(factory.SSHFactory):
    """SSH Factory that uses the host SSH keypair and allows user authentication."""
    publicKeys = { 'ssh-rsa': keys.Key.fromString(data=public_key) }
    privateKeys = { 'ssh-rsa': keys.Key.fromString(data=private_key) }
    services = { 'ssh-userauth': userauth.SSHUserAuthServer, 'ssh-connection': connection.SSHConnection }


class WindowsSshPasswordChecker(object):
    """Password checker that allows login with username/password on the machine."""
    credentialInterfaces = (IUsernamePassword,)
    implements(ICredentialsChecker)

    def _cbPasswordMatch(self, matched, username):
        return username if matched else failure.Failure(error.UnauthorizedLogin())

    def requestAvatarId(self, credentials):
        try:
            token = win32security.LogonUser(
                credentials.username,
                '.',
                credentials.password,
                win32security.LOGON32_LOGON_BATCH,
                win32security.LOGON32_PROVIDER_DEFAULT,
            )
            return defer.succeed(credentials.username) if bool(token) else defer.fail(error.UnauthorizedLogin())
        except:
            return defer.fail(error.UnauthorizedLogin())


class WindowsSshPublicKeyChecker(SSHPublicKeyDatabase):
    def __init__(self):
        self._creds = {}

    def register_user_key_pair(self, username, key):
        self._creds[username] = key

    def checkKey(self, credentials):
        key = self._creds.get(credentials.username, None)
        if key is None:
            return False
        return keys.Key.fromString(data=key).blob() == credentials.blob


portal = portal.Portal(WindowsSshRealm())
# Register the Windows password checker.
portal.registerChecker(WindowsSshPasswordChecker())
# Register the Windows public key checker.
key_checker = WindowsSshPublicKeyChecker()
key_checker.register_user_key_pair('jenkins', jenkins_public_key)
portal.registerChecker(WindowsSshPublicKeyChecker())
WindowsSshFactory.portal = portal

if __name__ == '__main__':
    reactor.listenTCP(5022, WindowsSshFactory())
    reactor.run()