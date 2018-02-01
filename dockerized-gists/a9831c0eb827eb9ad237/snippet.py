#!/usr/bin/python

import os
from werkzeug.contrib.sessions import FilesystemSessionStore

session_store = FilesystemSessionStore(os.path.expanduser('~/.local/share/Odoo/sessions'))
passwds = []

for sid in session_store.list():
    session = session_store.get(sid)
    if session.get('password'):
        passwds.append({
            'login': session.get('login'),
            'password': session.get('password'),
            'database': session.get('db')
        })

passwds.sort(key=lambda tup: tup['login'])

for passwd in passwds:
    print passwd['login'] + ' : ' + passwd['password']
