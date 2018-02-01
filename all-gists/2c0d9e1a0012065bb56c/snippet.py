#!/usr/bin/env python

import requests

from keystoneclient.contrib.auth.v3 import saml2
from keystoneclient import session


# project id you want to scope to
VALID_PROJECT_ID = 'your_project_id'

# IDP you have configured in Keystone
IDENTITY_PROVIDER = 'idp'

# ADFS URL you are supposed to send your SecurityTokenRequest
# /adfs/services/trust/13/usernamemixed is pretty standard suffix
# and is used for user/password authentication. So far we support only this
# authentication method in keystoneclient
IDENTITY_PROVIDER_URL = ("https://adfs.local/adfs/services/trust/13/"
                         "usernamemixed")

# Magic URL we are sending out assertion
SERVICE_PROVIDER_ENDPOINT = ("https://keystone.local:5000/Shibboleth.sso/ADFS")

# Place where unscoped federated token can be retrieved
SERVICE_PROVIDER_URL = ("https://keystone.local/v3/OS-FEDERATION/"
                        "identity_providers/%{IDP}s/protocols/saml2/auth")
SERVICE_PROVIDER_URL = SERVICE_PROVIDER_URL % {'IDP': IDENTITY_PROVIDER}
AUTH_URL = 'https://keystone.local:5000/v3'

saml2plugin = saml2.ADFSUnscopedToken(
    AUTH_URL, IDENTITY_PROVIDER,
    IDENTITY_PROVIDER_URL, SERVICE_PROVIDER_ENDPOINT,
    username='your_adfs_user', password='adfs_password')

s = session.Session(auth=None, verify=False, session=requests.Session())
token = saml2plugin.get_auth_ref(s)

# Scope the token

scopeTokenplugin = saml2.Saml2ScopedToken(
    AUTH_URL, token.auth_token,
    project_id=VALID_PROJECT_ID)

scoped_token = scopeTokenplugin.get_auth_ref(s)

print scoped_token
