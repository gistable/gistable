import gdata
import json
import requests

# More examples:
# https://github.com/millioner/Python-contact-importer/blob/master/contact_importer/providers/google.py
# https://github.com/jtauber/django-friends/blob/master/friends/importer.py

# GData with access token
token = gdata.gauth.OAuth2Token(
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    scope='https://www.google.com/m8/feeds',
    user_agent='app.testing',
    access_token=access_token)

contact_client = gdata.contacts.client.ContactsClient()
token.authorize(contact_client)

feed = contact_client.GetContacts()

for entry in feed.entry:
  entry.title.text
  for e in entry.email:
    e.address

# JSON with access token
r = requests.get('https://www.google.com/m8/feeds/contacts/default/full?access_token=%s&alt=json&max-results=50&start-index=0' % (access_token))
data = json.loads(r.text)