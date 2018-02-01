#!/usr/bin/env python3

import urllib.request
import re
import ssl
import sys

# # find generic mirrors
mirrors = urllib.request.urlopen('http://www.debian.org/mirror/list')
https = []
for line in mirrors.readlines():
    m = re.match(b'.*<td valign="top"><a rel="nofollow" href="http(.*)">.*', line)
    if m:
        url = 'https' + m.group(1).decode()
        print('trying: %s...' % url)
        sys.stdout.flush()
        try:
            response=urllib.request.urlopen(url, timeout=1)
            https.append(url)
            print('success!')
        except urllib.request.URLError as err:
            print('fail!')
        except ssl.SSLError as err:
            print('bad SSL!')
        except:
            print('bad stuff!!!')

# print('HTTPS apt repos:'
#for url in https:
#    print(url)


# # find security mirrors
mirrors = urllib.request.urlopen('http://www.debian.org/mirror/list-full')
securitys = []
for line in mirrors.readlines():
    m = re.match(b'.*</tt><br>Security updates over HTTP: <tt><a rel="nofollow" href="http(.*)">.*/debian-security/</a>.*', line)
    if m:
        url = 'https' + m.group(1).decode()
        print('trying: %s...' % url)
        sys.stdout.flush()
        try:
            response=urllib.request.urlopen(url, timeout=1)
            securitys.append(url)
            print('success!')
        except urllib.request.URLError as err:
            print('fail!')
        except ssl.SSLError as err:
            print('bad SSL!')

# print('HTTPS security repos:'
# for url in securitys:
#     print(url)


# now find the backports mirrors
try:
        mirrors = urllib.request.urlopen('http://backports-master.debian.org/Mirrors/')
except:
        print('URL open failed!!!')
backports = []
for line in mirrors.readlines():
#<td><a href="http://be.mirror.eurid.eu/debian-backports/">/debian-backports/</a>
    m = re.match(b'.*<td><a href="http(.*)">.*/debian-backports/</a>.*', line)
    if m:
        url = 'https' + m.group(1).decode()
        print('trying: %s...' % url)
        sys.stdout.flush()
        try:
            response=urllib.request.urlopen(url, timeout=1)
            backports.append(url)
            print('success!')
        except urllib.request.URLError as err:
            print('fail!')
        except ssl.SSLError as err:
            print('bad SSL!')

#print('HTTPS backports repos:'
#for url in backports:
#    print(url)


# now find the CD image mirrors
mirrors = urllib.request.urlopen('http://www.debian.org/CD/http-ftp/')
cds = []
for line in mirrors.readlines():
# <a rel="nofollow" href="http://mirror.easyspeedy.com/debian-cd/">HTTP</a></li>
    m = re.match(b'.*<a rel="nofollow" href="http(:.*)">HTTP</a></li>.*', line)
    if m:
        url = 'https' + m.group(1).decode()
        print('trying: %s...' % url)
        sys.stdout.flush()
        try:
            response=urllib.request.urlopen(url, timeout=1)
            cds.append(url)
            print('success!')
        except urllib.request.URLError as err:
            print('fail!')
        except ssl.SSLError as err:
            print('bad SSL!')
        except:
            print('bad stuff!')

print('HTTPS CD image repos:')
for url in cds:
    print(url)


# now write everything to a file
dst_filename='/tmp/https-debian-archives.txt'
f = open(dst_filename, 'w')
print('Outputfile: "%s"' % dst_filename)

f.write('HTTPS apt repos\n')
f.write('---------------\n')
for url in https:
    f.write(url + '\n')

f.write('\n\nHTTPS security repos\n')
f.write('---------------\n')
for url in securitys:
    f.write(url + '\n')

f.write('\n\nHTTPS backports repos\n')
f.write('--------------------\n')
for url in backports:
    f.write(url + '\n')

f.write('\n\nHTTPS CD image repos\n')
f.write('--------------------\n')
for url in cds:
    f.write(url + '\n')


f.close()
