# settings
settings = {...}

# authentication
from eve.auth import TokenAuth
import requests
from flask import request, g
class TokenAuth(TokenAuth):
    def check_auth(self, token, allowed_roles, resource, method):
        # check token against user api
        try:
            r = requests.get('http://user-api/', params={'token':token}, verify=False)
            data = r.json()
            if data['authenticated'] == True:
                g.user = data['user']['id']
                return True
        except:
            print 'Uh oh, I cannot communicate to the user API!'

        return False

# auto fill _created_by and _modified_by user fields
created_by_field = '_created_by'
modified_by_field = '_modified_by'
for resource in settings['DOMAIN']:
    settings['DOMAIN'][resource]['schema'][created_by_field] = {'type': 'string'}
    settings['DOMAIN'][resource]['schema'][modified_by_field] = {'type': 'string'}
def before_insert(resource, documents):
    user = g.get('user', None)
    if user is not None:
        for document in documents:
            document[created_by_field] = user
            document[modified_by_field] = user
def before_replace(resource, document):
    user = g.get('user', None)
    if user is not None:
        document[modified_by_field] = user

# create eve app
from eve import Eve
app = Eve(settings=settings, auth=TokenAuth)
app.on_insert += before_insert
app.on_replace += before_replace