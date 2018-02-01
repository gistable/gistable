#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

import base64, os, fcntl, tty, struct

from twisted.enterprise import adbapi

from twisted.cred import portal, checkers, credentials
from twisted.conch import error, avatar
from twisted.conch.unix import SSHSessionForUnixConchUser,UnixConchUser
from twisted.conch.checkers import SSHPublicKeyDatabase
from twisted.conch.ssh import factory, userauth, connection, keys, session
from twisted.internet import reactor, protocol, defer
from twisted.python import log
from zope.interface import implements
from twisted.python import components, failure

import sys
log.startLogging(sys.stderr)

# ホスト公開鍵
publicKey  = 'ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAGEArzJx8OYOnJmzf4tfBEvLi8DVPrJ3/c9k2I/Az64fxjHf9imyRJbixtQhlH9lfNjUIx+4LmrJH5QNRsFporcHDKOTwTTYLh5KmRpslkYHRivcJSkbh/C+BR3utDS555mV'
# ホスト秘密鍵
privateKey = """-----BEGIN RSA PRIVATE KEY-----
MIIByAIBAAJhAK8ycfDmDpyZs3+LXwRLy4vA1T6yd/3PZNiPwM+uH8Yx3/YpskSW
4sbUIZR/ZXzY1CMfuC5qyR+UDUbBaaK3Bwyjk8E02C4eSpkabJZGB0Yr3CUpG4fw
vgUd7rQ0ueeZlQIBIwJgbh+1VZfr7WftK5lu7MHtqE1S1vPWZQYE3+VUn8yJADyb
Z4fsZaCrzW9lkIqXkE3GIY+ojdhZhkO1gbG0118sIgphwSWKRxK0mvh6ERxKqIt1
xJEJO74EykXZV4oNJ8sjAjEA3J9r2ZghVhGN6V8DnQrTk24Td0E8hU8AcP0FVP+8
PQm/g/aXf2QQkQT+omdHVEJrAjEAy0pL0EBH6EVS98evDCBtQw22OZT52qXlAwZ2
gyTriKFVoqjeEjt3SZKKqXHSApP/AjBLpF99zcJJZRq2abgYlf9lv1chkrWqDHUu
DZttmYJeEfiFBBavVYIF1dOlZT0G8jMCMBc7sOSZodFnAiryP+Qg9otSBjJ3bQML
pSTqy7c3a2AScC/YyOwkDaICHnnD3XyjMwIxALRzl0tQEKMXs6hH8ToUdlLROCrP
EhQ0wahUTCk1gKA4uPD6TMTChavbh4K63OvbKg==
-----END RSA PRIVATE KEY-----"""

class PublicKeyCredentialsChecker:
    implements(checkers.ICredentialsChecker)
    credentialInterfaces = (credentials.ISSHPrivateKey,)

    def __init__(self, dbpool):
      self.dbpool = dbpool

    def requestAvatarId(self, credentials):
        publickey = base64.b64encode(credentials.blob)
        print publickey
        # SQL Injection ...
        defer = self.dbpool.runQuery("SELECT account FROM publickeys WHERE publickey = '%s'" % publickey)
        defer.addCallback(self._cbRequestAvatarId, credentials)
        defer.addErrback(self._ebRequestAvatarId)

        # return "sqale" とか変えすと認証無条件で通る
        return defer

    # TODO
    def _cbRequestAvatarId(self, result, credentials):
        if result:
            return result[0][0]
        else:
            f = failure.Failure()
            log.err()
            return f

    # TODO
    def _ebRequestAvatarId(self, f):
        return f

class ProxySSHUser(avatar.ConchUser):

    def __init__(self, username):
        avatar.ConchUser.__init__(self)
        self.username = username
        self.channelLookup.update({'session':session.SSHSession})

    # Mac
    def getUserGroupId(self):
        return 502,20

class ProxySSHRealm:
    implements(portal.IRealm)

    def requestAvatar(self, avatarId, mind, *interfaces):
        return interfaces[0], ProxySSHUser(avatarId), lambda: None
    
class ProxySSHSession(SSHSessionForUnixConchUser):

    def openShell(self, proto):
        uid, gid = self.avatar.getUserGroupId()
        command = "/usr/bin/ssh"
        args    = ["ssh", "-p 22", "example.com"]
        self.pty = reactor.spawnProcess(proto, command, args, self.environ, "/", uid, gid, usePTY=self.ptyTuple)
        # 画面幅を調整
        fcntl.ioctl(self.pty.fileno(), tty.TIOCSWINSZ, struct.pack('4H', *self.winSize))
        self.avatar.conn.transport.transport.setTcpNoDelay(1)

class ProxySSHFactory(factory.SSHFactory):

    publicKeys  = { 'ssh-rsa': keys.Key.fromString(data=publicKey)   }
    privateKeys = { 'ssh-rsa': keys.Key.fromString(data=privateKey) }
    services = {
        'ssh-userauth': userauth.SSHUserAuthServer,
        'ssh-connection': connection.SSHConnection
    }

if __name__ == '__main__':

    dbpool = adbapi.ConnectionPool("MySQLdb", db='test', host='localhost', user='root')

    # セッションを登録
    portal = portal.Portal(ProxySSHRealm())
    components.registerAdapter(ProxySSHSession, ProxySSHUser, session.ISession)
    portal.registerChecker(PublicKeyCredentialsChecker(dbpool))
    ProxySSHFactory.portal = portal

    reactor.listenTCP(5022, ProxySSHFactory())
    reactor.run()
