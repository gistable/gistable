import os
import gdata
import atom
import gdata.contacts
import gdata.contacts.service
import dataset

import requests
from lxml import html
from urlparse import urljoin, parse_qs

BASE_URL = 'http://pgp.mit.edu/pks/lookup'
db = dataset.connect('sqlite:///stats.db')
table = db['stats']

def make_client():
    gd_client = gdata.contacts.service.ContactsService()
    gd_client.email = os.environ.get('GOOGLE_USER')
    gd_client.password = os.environ.get('GOOGLE_PASS')
    gd_client.source = 'gpg-loader-sync'
    gd_client.ProgrammaticLogin()
    return gd_client

def get_emails():
    gd_client = make_client()
    url = None
    while True:
        feed = gd_client.GetContactsFeed(url)
        for contact in feed.entry:
            for email in contact.email:
                yield contact, email.address

        url = feed.GetNextLink().href


def search_email(email):
    res = requests.get(BASE_URL,
            params={'search': email, 'op': 'index', 'exact': 'on'})
    doc = html.fromstring(res.content)
    print [email]
    for pre in doc.findall('.//pre'):
        text = pre.xpath('string()')
        if '*** KEY REVOKED ***' in text:
            continue
        if not email in text:
            continue
        for a in pre.findall('.//a'):
            url = a.get('href')
            if 'op=get' in url:
                qs = url.split('?')[-1]
                data = parse_qs(qs)
                url = urljoin(BASE_URL, url)
                res = requests.get(url)
                idoc = html.fromstring(res.content)
                key = idoc.find('.//pre').text
                yield data.get('search')[0], key

def save_key(key_id, key):
    fn = os.path.join('keys', key_id + '.gpg')
    with open(fn, 'wb') as fh:
        fh.write(key)

def store_stats(data, **kw):
    d = data.copy()
    d.update(kw)
    if d['title']:
        d['title'] = d['title'].decode('utf-8')
    table.upsert(d, ['uri', 'key_id'])

if __name__ == '__main__':
    if not os.path.isdir('keys'):
        os.makedirs('keys')
    for contact, email in get_emails():
        stored = False
        _, domain = email.rsplit('@', 1)
        data = {
            'email': email,
            'domain': domain,
            'title': contact.title.text,
            'uri': contact.id.text,
            'key_id': None
            }
        try:
            for key_id, key in search_email(email):
                save_key(key_id, key)
                store_stats(data, key_id=key_id)
                stored = True
                print key_id
        except Exception, e:
            print e
        if not stored:
            store_stats(data)
