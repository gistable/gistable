# Here's how I got this to work:
# 1. Download this client library into your GAE project: 
#   https://developers.google.com/api-client-library/python/start/installation#appengine
#   https://code.google.com/p/google-api-python-client/downloads/detail?name=google-api-python-client-gae-1.2.zip&can=2&q=
# 2. Copy this file from the GAE SDK installed on your development machine
#   google/appengine/tools/appengine_rpc_httplib2.py
# 3. Modify the import statements as necessary
# 4. Create a secrets.py file that defines a appcfg_refresh_token property
# 5. Obtain the refresh token by
#   Calling appcfg.py list_versions . --oauth2, this will open a browser so you can login with your Google Account
#   Find and copy the refresh_token from ~/.appcfg_oauth2_tokens
# 6. Create a handler that calls this list_version() command, upload to GAE, and fire away!

import yaml

from third_party.google_api_python_client import appengine_rpc_httplib2

# NOTE: You must defined your own secrets.py file with the 
import secrets
import layer_cache

# Not-so-secret IDs cribbed from appcfg.py
# https://code.google.com/p/googleappengine/source/browse/trunk/python/google/appengine/tools/appcfg.py#144
APPCFG_CLIENT_ID = '550516889912.apps.googleusercontent.com'
APPCFG_CLIENT_NOTSOSECRET = 'ykPq-0UYfKNprLRjVx1hBBar'
APPCFG_SCOPES = ['https://www.googleapis.com/auth/appengine.admin']


def get_rpc_server():
    """Constructs an HttpRpcServerOauth2 object impersonating the
    account's refresh token specified in secrets.py.

    This code was cribbed directly from appcfg.py.
    """
    source = (APPCFG_CLIENT_ID,
                APPCFG_CLIENT_NOTSOSECRET,
                APPCFG_SCOPES,
                None)

    rpc_server = appengine_rpc_httplib2.HttpRpcServerOauth2(
        'appengine.google.com',
        # NOTE: Here's there the refresh token is used
        secrets.appcfg_refresh_token,
        "appcfg_py/1.8.3 Darwin/12.5.0 Python/2.7.2.final.0",
        source,
        host_override=None,
        save_cookies=False,
        auth_tries=1,
        account_type='HOSTED_OR_GOOGLE',
        secure=True,
        ignore_certs=False)

    return rpc_server


def list_versions():
    """Returns a dictionary object with modules and their deployed versions.

    Looks like: {
        "default": [
            "1025-0e42046ea0fd-highmembackend",
            "1025-0e42046ea0fd-mapreducebackend",
            "ah-builtin-python-bundle",
            "staging",
        ]
    }
    """
    rpc_server = get_rpc_server()
    # NOTE: You must insert the correct app_id here, too
    response = rpc_server.Send('/api/versions/list', app_id="khan-academy")

    # The response is in YAML format
    parsed_response = yaml.safe_load(response)
    if not parsed_response:
        return None
    else:
        return parsed_response