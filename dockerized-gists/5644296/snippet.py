#!/usr/bin/python

# http://www.packtpub.com/article/python-ldap-applications-ldap-opearations

# sudo apt-get install python-ldap

import ldap

host = 'ldap://example.com:389'
dn = 'ldap@example.com'
pw = 'secret'
base_dn = 'cn=users,dc=example,dc=com'
filter = 'memberOf=cn=workers,cn=users,dc=example,dc=com'
# Show only activated users
# filter = '(&(memberOf=cn=workers,cn=users,dc=example,dc=com)(!(userAccountControl=66050)))'
attrs = ['sAMAccountName', 'givenname', 'sn', 'mail', 'description', 'telephonenumber', 'homephone', 'mobile']
 
con = ldap.initialize( host )

# Bind to the server
con.simple_bind_s( dn, pw )

res = con.search_s( base_dn, ldap.SCOPE_SUBTREE, filter, attrs )

# Close the connection
con.unbind()

# Print the returned dictionary
print res

for i in res:
    print i[1]['givenname'], i[1]['sn']

# TODO: save as csv file