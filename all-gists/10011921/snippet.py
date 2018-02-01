'''
Created on Mar 18, 2014
@author: OAuth2 base code 'jcgregorio@google.com (Joe Gregorio)' 
@author modificaciones: nickbortolotti
'''

from apiclient import discovery
from oauth2client import appengine
from oauth2client import client
from google.appengine.api import memcache

import webapp2
import jinja2
import httplib2
import os


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    autoescape=True,
    extensions=['jinja2.ext.autoescape'])

# CLIENT_SECRETS, name of a file containing the OAuth 2.0 information for this
# application, including client_id and client_secret, which are found
# on the API Access tab on the Google APIs
# Console <http://code.google.com/apis/console>
CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')

# Helpful message to display in the browser if the CLIENT_SECRETS file
# is missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
<h1>Por favor configure OAuth 2.0</h1>
<p>
<code>%s</code>.
</p>
""" % CLIENT_SECRETS


http = httplib2.Http(memcache)
service = discovery.build("plus", "v1", http=http)
decorator = appengine.oauth2decorator_from_clientsecrets(
    CLIENT_SECRETS,
    scope='https://www.googleapis.com/auth/plus.me',
    message=MISSING_CLIENT_SECRETS_MESSAGE)

class MainHandler(webapp2.RequestHandler):

    @decorator.oauth_aware
    def get(self):
        variables = {
                     'url': decorator.authorize_url(),
                     'has_credentials': decorator.has_credentials()
                     }
        template = JINJA_ENVIRONMENT.get_template('conceder.html')
        self.response.write(template.render(variables))


class Social(webapp2.RequestHandler):

    @decorator.oauth_required
    def get(self):
        try:
            http = decorator.http()
            user = service.people().get(userId='me').execute(http=http)
            text = 'Hola, %s!' % user['displayName']
            image = user['image']['url']
            cover = user['cover']['coverPhoto']['url']

            template = JINJA_ENVIRONMENT.get_template('bienvenido.html')
            self.response.write(template.render({'text': text,
                                                 'image': image,
                                                 'cover': cover 
                                                 }))
        except client.AccessTokenRefreshError:
            self.redirect('/')


application = webapp2.WSGIApplication(
    [
     ('/', MainHandler),
     ('/social', Social),
     (decorator.callback_path, decorator.callback_handler()),
    ],
    debug=True)