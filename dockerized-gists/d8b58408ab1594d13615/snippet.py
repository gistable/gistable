import sys, ldap

# DN = username@example.com, secret = password, un = username
DN, secret, un = sys.argv[1:4]

server = "ldap://server.com"
port = 389

base = "dc=example,dc=com"
scope = ldap.SCOPE_SUBTREE
filter = "(&(objectClass=user)(sAMAccountName=" + un + "))"
attrs = ["*"]

l = ldap.initialize(server)
l.protocol_version = 3
l.set_option(ldap.OPT_REFERRALS, 0)

print l.simple_bind_s(DN, secret)

r = l.search(base, scope, filter, attrs)
type, user = l.result(r, 60)

name, attrs = user[0]

if hasattr(attrs, 'has_key') and attrs.has_key('displayName'):
    print attrs

sys.exit()