#!/usr/bin/env python

from zope.interface import implements
from twisted.cred import portal, checkers, credentials, error as credError
from twisted.internet import defer, reactor
from twisted.web import static, resource
from twisted.web.resource import IResource
from twisted.web.http import HTTPChannel
from twisted.web import server
from twisted.web.guard import HTTPAuthSessionWrapper
from twisted.web.guard import DigestCredentialFactory
from twisted.web.guard import BasicCredentialFactory

class PasswordDictChecker:
    implements(checkers.ICredentialsChecker)
    credentialInterfaces = (credentials.IUsernamePassword,)

    def __init__(self, passwords):
        "passwords: a dict-like object mapping usernames to passwords"
        self.passwords = passwords

    def requestAvatarId(self, credentials):
        username = credentials.username
        if self.passwords.has_key(username):
            if credentials.password == self.passwords[username]:
                return defer.succeed(username)
            else:
                return defer.fail(
                    credError.UnauthorizedLogin("Bad password"))
        else:
            return defer.fail(
                credError.UnauthorizedLogin("No such user"))

class HttpPasswordRealm(object):
    implements(portal.IRealm)

    def __init__(self, myresource):
        self.myresource = myresource
    
    def requestAvatar(self, user, mind, *interfaces):
        if IResource in interfaces:
            # myresource is passed on regardless of user
            return (IResource, self.myresource, lambda: None)
        raise NotImplementedError()

class MyResource(resource.Resource):

    def __init__(self):
        resource.Resource.__init__(self)

    def getChild(self, path, request):
        text = "You're in.  The path is /%s." % path
        return static.Data(text, "text/plain")

passwords = {
    'admin': 'aaa',
    'user1': 'bbb',
    'user2': 'ccc'
    }

if __name__ == "__main__":
    myresource = MyResource()

    checker = PasswordDictChecker(passwords)
    realm = HttpPasswordRealm(myresource)
    p = portal.Portal(realm, [checker])

    credentialFactory = BasicCredentialFactory("McLaren Labs")
    protected_resource = HTTPAuthSessionWrapper(p, [credentialFactory])

    root = resource.Resource()
    root.putChild("example", protected_resource)

    site = server.Site(root)
    site.protocol = HTTPChannel

    reactor.listenTCP(8801, site)
    reactor.run()
