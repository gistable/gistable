'''
Syncthing integration for Caja (MATE file manager)

1) Put it into ~/.local/share/caja-python/extensions

2) Install python-caja:
    # sudo apt-get install python-caja

3) Install python-requests:
    $ sudo add-apt-repository ppa:deluge-team/ppa
    $ sudo apt-get install requests
OR:
    $ sudo pip install requests

4) Set your Syncthing URL and API-key:
'''
REST_URL = 'http://localhost:8080/rest'
API_KEY = 'INSERT_YOUR_API_KEY_HERE'


from gi.repository import Caja, GObject
import os
import json
import urllib
import requests


def _get_item_path(item):
    uri_raw = item.get_uri()
    if len(uri_raw) < 7:
        return ''
    return os.path.normpath(urllib.unquote(uri_raw[7:]))


def _get_dir_path(item):
    dir_path = _get_item_path(item)
    if os.path.isfile(dir_path):
        dir_path = os.path.dirname(dir_path)
    return dir_path


def _get_conf():
    resp = requests.get(REST_URL + '/config')
    return resp.json()


def _set_conf(conf):
    resp = requests.post(REST_URL + '/config', json.dumps(conf), headers={'X-API-Key': API_KEY})
    restarted = requests.post(REST_URL + '/restart', headers={'X-API-Key': API_KEY})
    return restarted


def _get_synced_dirs(conf):
    return {i['ID']: os.path.normpath(i['Path']) for i in conf['Folders']}


class SyncthingMenuProvider(GObject.GObject, Caja.InfoProvider, Caja.MenuProvider):
    def __init__(self):
        """Caja crashes if a plugin doesn't implement the __init__ method"""
        pass

    def _is_server_online(self):
        try:
            r = requests.get(REST_URL + '/ping').json()
            return True
        except requests.ConnectionError as e:
            return False

    # ================= InfoProvider ======================

    def update_file_info(self, item):
        if item.get_uri_scheme() != 'file':
            return

        synced_dirs = _get_synced_dirs(_get_conf())
        item_path = _get_item_path(item)
        if item_path in synced_dirs.values():
            item.add_emblem('synchronizing')

    # ================= MenuProvider ======================

    def get_file_items(self, window, sel_items):
        if len(sel_items) != 1 or sel_items[0].get_uri_scheme() != 'file':
            return
        if not self._is_server_online():
            return

        synced_dirs = _get_synced_dirs(_get_conf())
        dir_path = _get_item_path(sel_items[0])
        if dir_path in synced_dirs.values():
            item = Caja.MenuItem(name='CajaSyncthing::dir_rm',
                                     label='Remove Directory from Syncthing',
                                     tip='Remove selected directory from syncthing',
                                     icon='emblem-synchronizing')
            item.connect('activate', self.on_dir_rm, sel_items[0])
        else:
            item = Caja.MenuItem(name='CajaSyncthing::dir_add',
                                     label='Add Directory to Syncthing',
                                     tip='Add selected directory to syncthing',
                                     icon='emblem-synchronizing')
            item.connect('activate', self.on_dir_add, sel_items[0])
        return [item]

    def get_background_items(self, window, current_directory):
        if not self._is_server_online():
            return

        synced_dirs = _get_synced_dirs(_get_conf())
        dir_path = _get_item_path(current_directory)
        if dir_path in synced_dirs.values():
            item = Caja.MenuItem(name='CajaSyncthing::curr_dir_rm',
                                     label='Remove Current Directory from Syncthing',
                                     tip='Remove current directory from syncthing',
                                     icon='emblem-synchronizing')
            item.connect('activate', self.on_dir_rm, current_directory)
        else:
            item = Caja.MenuItem(name='CajaSyncthing::curr_dir_add',
                                     label='Add Current Directory to Syncthing',
                                     tip='Add current directory to syncthing',
                                     icon='emblem-synchronizing')
            item.connect('activate', self.on_dir_add, current_directory)
        return [item]

    def on_dir_add(self, menu, selected):
        dir_path = _get_dir_path(selected)
        dir_id = os.path.basename(dir_path)

        conf = _get_conf()
        synced_dirs = _get_synced_dirs(conf)
        if (dir_id in synced_dirs.keys()) or (dir_path in synced_dirs.values()):
            return

        conf['Folders'].append({'ID': dir_id, 'Path': dir_path})

        _set_conf(conf)

    def on_dir_rm(self, menu, selected):
        dir_path = _get_dir_path(selected)

        conf = _get_conf()
        synced_dirs = _get_synced_dirs(conf)
        if dir_path in synced_dirs.values():
            for f in conf['Folders']:
                if f['Path'] == dir_path:
                    conf['Folders'].remove(f)

        _set_conf(conf)
