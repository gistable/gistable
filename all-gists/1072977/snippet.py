############################## django-auth-ldap ##############################
import ldap
from django_auth_ldap.config import LDAPSearch, PosixGroupType

# django-auth-ldap configuration starts here
AUTH_LDAP_SERVER_URI = "ldap://ldap.els03.loc ldap://ldap.zbw03.loc ldap://ldap.cvg03.loc"

#AUTH_LDAP_USER_DN_TEMPLATE = "uid=%(user)s,ou=People,o=loc"
# JW is in ou=Admin,o=loc so we search over o=loc to find him
AUTH_LDAP_USER_SEARCH = LDAPSearch("o=loc",
   ldap.SCOPE_SUBTREE, "(uid=%(user)s)")

# Set up the basic group parameters.
AUTH_LDAP_GROUP_SEARCH = LDAPSearch("ou=Groups,o=loc",
   ldap.SCOPE_SUBTREE, "(objectClass=posixGroup)"
)
AUTH_LDAP_GROUP_TYPE = PosixGroupType()

# Only users in this group can log in.
AUTH_LDAP_REQUIRE_GROUP = "cn=it,ou=Groups,o=loc"

# Populate the Django user from the LDAP directory.
AUTH_LDAP_USER_ATTR_MAP = { 
   "first_name": "givenName",
   "last_name":  "sn",
   "email":      "mail"
}

# Users in the reconro group who are *not* in it, or neteng
# will have to be manually activated by someone with  admin
# privileges manually. Do it from http://netrecon.loc/admin
AUTH_LDAP_USER_FLAGS_BY_GROUP = { 
   "is_active":    "cn=it,ou=Groups,o=loc",
   "is_staff":     "cn=neteng,ou=Groups,o=loc",
   "is_superuser": "cn=admin,ou=Groups,o=loc",
}

# This should only be done once
AUTH_LDAP_ALWAYS_UPDATE_USER = False

# Use LDAP group membership to calculate group permissions.
AUTH_LDAP_FIND_GROUP_PERMS = True

# Cache group memberships for an hour to minimize LDAP traffic
AUTH_LDAP_CACHE_GROUPS = True
AUTH_LDAP_GROUP_CACHE_TIMEOUT = 3600

# Use ldaps:// because it is mo'betta
AUTH_LDAP_START_TLS = True

# Keep ModelBackend around for per-user permissions and maybe a local
# superuser.
AUTHENTICATION_BACKENDS = ( 
   'django_auth_ldap.backend.LDAPBackend',
   'django.contrib.auth.backends.ModelBackend',
)
############################ end django-auth-ldap ############################
