#!/usr/bin/env python3

"""
Extract archives from a Deluge download and then call Rad/Sonarr to import the files.

Extra files (as configured in radarr or sonarr) are also copied to the
extraction directory.

This script has been tested with:
    - Linux (tested with Arch)
        - unzip and unrar are required: `pacman -Sy unzip unrar`
    - Python 3: `pacman -Sy python python-pip`
        - Requests is required: `pip install requests`
    - Deluge with Label and Execute plugins
    - Sonarr and Radarr

Usage on a different environment may require additional tweaks. MAKE SURE THE
EXECUTABLE BIT IS SET ON THIS FILE.
"""

from collections import namedtuple
from glob import iglob
import os
import requests
import shutil
from syslog import syslog
import sys

# -- Configs
commands = {'zip': 'unzip -u', 'rar': 'unrar -o- e'}
extraction_root = '/data/downloads/extracted'

# Make sure the deluge, radarr and sonarr users are in the download group
# otherwise the Move operation will not be able to complete.
download_group = 'downloads'

deluge = namedtuple('DelugeConfig', 'url password session_id')
deluge.url = 'http://localhost:31337/json'
deluge.password = ''

sonarr = namedtuple('SonarrConfig', 'url api_key label')
sonarr.url = 'http://localhost:31338/api'
sonarr.api_key = ''
sonarr.label = 'sonarr'

radarr = namedtuple('RadarrConfig', 'url api_key label')
radarr.url = 'http://localhost:31339/api'
radarr.api_key = ''
radarr.label = 'radarr'

# -- Arguments
torrent = namedtuple('Torrent', 'id name path dir label')
torrent.id = sys.argv[1]
torrent.name = sys.argv[2]
torrent.path = sys.argv[3]
torrent.dir = os.path.join(torrent.path, torrent.name)
torrent.label = ''

syslog(torrent.id + ' - Preparing torrent for extraction: ' + torrent.dir)


def update_rights(path, group, mode=0o664):
    shutil.chown(path, group=group)
    os.chmod(path, mode)


# -- Fetch torrent label
syslog(torrent.id + ' - Authenticating into deluge.')

auth_headers = {'content-type': 'application/json', 'accept': 'application/json'}
auth_data = {'method': 'auth.login', 'params': [deluge.password], 'id': 1}
response = requests.post(deluge.url, json=auth_data, headers=auth_headers)

if response.status_code != 200 and not response.json()['result']:
    sys.exit('Unable to authenticate to deluge')

deluge.session_id = response.cookies['_session_id']

syslog(torrent.id + ' - Got deluge session ID ' + deluge.session_id)
syslog(torrent.id + ' - Fetching torrent label from deluge.')

info_headers = {'content-type': 'application/json', 'accept': 'application/json'}
info_cookies = dict(_session_id=deluge.session_id)
info_data = {'method': 'web.get_torrent_status', 'params': [torrent.id, ['label']], 'id': 1}
response = requests.post(deluge.url, json=info_data, headers=info_headers, cookies=info_cookies)

if response.status_code != 200:
    sys.exit('Unable to fetch torrent label')

torrent.label = response.json()['result']['label']

syslog(torrent.id + ' - Got torrent label: ' + torrent.label)

pvr = next((x for x in (sonarr, radarr) if x.label == torrent.label), None)

if not pvr:
    syslog(torrent.id + ' - Not a Sonarr/Radarr tracked download. Skipping extraction.')
    sys.exit(0)

# -- Extract files
extraction_dir = os.path.join(extraction_root, torrent.name)
extracted = False
if not os.path.isdir(extraction_dir):
    os.makedirs(extraction_dir)
    update_rights(extraction_dir, download_group, 0o775)

os.chdir(torrent.dir)
for ext, command in commands.items():
    for file in iglob('*.' + ext):
        file_path = os.path.join(torrent.dir, file)
        syslog('Extracting ' + file_path + ' to ' + extraction_dir)

        # TODO: How to handle extraction errors (ie: CRC errors)?
        os.system(command + ' "' + file + '" "' + extraction_dir + '"')
        extracted = True

if not extracted:
    syslog(torrent.id + ' - Nothing to extract.')
    sys.exit(0)

# -- Copy extra files (srt, nfo, ...)
syslog(torrent.id + ' - Fetching extra file types to copy.')

extras_headers = {'accept': 'application/json', 'X-Api-Key': pvr.api_key}
response = requests.get(pvr.url + '/config/mediamanagement', headers=extras_headers)

extra_file_types = response.json()['extraFileExtensions']

syslog(torrent.id + ' - Copying extra files: ' + extra_file_types)
for ext in extra_file_types.split(','):
    for file in iglob('*.' + ext):
        shutil.copy2(file, extraction_dir)

# -- Change owner and mode so sonarr/radarr can move the files
syslog(torrent.id + ' - Updating extracted files permissions.')
for root, dirs, files in os.walk(extraction_dir):
    for file in files:
        update_rights(os.path.join(root, file), download_group)
    for dir in dirs:
        update_rights(os.path.join(root, dir), download_group)

# -- Notify Sonarr/Radarr
notify_headers = {'content-type': 'application/json', 'accept': 'application/json', 'X-Api-Key': pvr.api_key}
notify_data = {'name': 'DownloadedEpisodesScan', 'importMode': 'Move', 'downloadClientId': torrent.id.upper(),
               'path': extraction_dir}

syslog(torrent.id + ' - Asking PVR API to scan extracted files.')

response = requests.post(pvr.url + '/command', json=notify_data, headers=notify_headers)

if not response.status_code >= 200 and response.status_code < 300:
    sys.exit('Could not notify Sonarr/Radarr of extracted file.')
