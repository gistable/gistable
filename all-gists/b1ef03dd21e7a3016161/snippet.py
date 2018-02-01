#!/usr/bin/env python
"""

Sample call:
python synapse_galaxy_sync.py <api_key> <api_url> syn12345

NOTE:  The upload method used requires the data library filesystem upload allow_library_path_paste
"""
import os
import shutil
import sys
import re
import json
import time
import requests
import synapseclient

    
class RemoteGalaxy(object):

    def __init__(self, url, api_key):
        self.url = url
        self.api_key = api_key

    def get(self, path):
        c_url = self.url + path
        params = {}
        params['key'] = self.api_key
        req = requests.get(c_url, params=params)
        return req.json()

    def post(self, path, payload):
        c_url = self.url + path
        params = {}
        params['key'] = self.api_key
        print "POSTING", c_url, json.dumps(payload)
        req = requests.post(c_url, data=json.dumps(payload), params=params, headers = {'Content-Type': 'application/json'} )
        return req.json()

    def post_text(self, path, payload, params=None):
        c_url = self.url + path
        if params is None:
            params = {}
        params['key'] = self.api_key
        print "POSTING", c_url, json.dumps(payload)
        req = requests.post(c_url, data=json.dumps(payload), params=params, headers = {'Content-Type': 'application/json'} )
        return req.text
    

class LibrarySync:
    def __init__(self, remote_galaxy, library_name):
        self.remote_galaxy = remote_galaxy
        res = remote_galaxy.post("/api/search", {"query" : "select * from library where name='%s' and deleted=False" % (library_name)})
        if 'error' in res:
            raise Exception(res['error'])
        library_id = None
        for row in res['results']:
            library_id = row['id']
        if library_id is None:
            lib_create_data = {'name':library_name}
            library = remote_galaxy.post('/api/libraries', lib_create_data)
            library_id = library['id']       
        self.library_id = library_id
        self.path_map = {}
    
    def get_library_folder_id(self, folder):
        library_path = "/" + "/".join(folder)
        if library_path not in self.path_map:
            res = self.remote_galaxy.post("/api/search", {"query" : "select * from library_folder where library_path='%s' and parent_library_id='%s'" % (library_path, self.library_id)})
            if 'error' in res:
                raise Exception(res['error'])
            id_value = None
            for row in res['results']:
                id_value = row['id']
            if id_value is not None:
                self.path_map[library_path] = id_value
            else:
                parentId = self.get_library_folder_id(folder[:-1])
                if parentId is not None:
                    create_request = { "create_type" : 'folder', 'folder_id' : parentId, 'name' : folder[-1] }
                    res = self.remote_galaxy.post("/api/libraries/%s/contents" % (self.library_id), create_request)
                    print "Created Folder:", res
                    id_value = res[0]['id'][1:] #remove preceeding F (why do I have to do this?)
                    self.path_map[library_path] = id_value
                else:
                    return None
        return self.path_map[library_path]

    def get_library_dataset_id(self, folder_id, dataset_name):
        res = self.remote_galaxy.post("/api/search", {'query' : "select * from library_dataset where folder_id='%s' and name='%s'" % (folder_id, dataset_name)} )
        if 'error' in res:
            raise Exception(res['error'])
        dataset_id = None
        for row in res['results']:
            dataset_id = row['id']
        return dataset_id
        
    def library_paste_file(self, library_folder_id, name, meta, datapath):
        data = {}
        data['folder_id'] = library_folder_id
        data['file_type'] = 'auto'
        data['name'] = name
        data['dbkey'] = ''
        data['upload_option'] = 'upload_paths'
        data['create_type'] = 'file'
        data['link_data_only'] = 'link_to_files'
        data['extended_metadata'] = meta                         
        data['filesystem_paths'] = datapath
        libset = self.remote_galaxy.post("/api/libraries/%s/contents" % self.library_id, data)
        return libset

    def item_rename(self, library_folder_id, item_id, name, info, message):
            #rename the entry
            #/library_common/ldda_edit_info?library_id=03501d7626bd192f&show_deleted=False&cntrller=library_admin&folder_id=7ca8f1b7f24e5a2d&use_panels=False
            self.remote_galaxy.post_text( "/library_common/ldda_edit_info", 
                {                   
                    'name' : name,
                    'message' : message,
                    'info' : info 
                }, 
                {
                    'show_deleted' : 'False',
                    'cntrller' : 'library_admin',
                    'folder_id' : library_folder_id,
                    'id' : item_id, 
                    'use_panels' : 'False',
                     'library_id' : self.library_id, 
                }
            )


def project_scan(syn, synapse_project, galaxy_library, base_path=[]):
    ent = syn.getEntity(synapse_project)
    cur_path = base_path + [ent['name']]
    print "Entering", "/".join(cur_path)
    for res in syn.query("select * from entity where parentId=='%s'" % (synapse_project))['results']:
        if res['entity.nodeType'] in [ 0, 4 ]:
            project_scan(syn, res['entity.id'], galaxy_library, cur_path)
        elif res['entity.nodeType'] in [1, 16]:
            new_dir = cur_path + [res['entity.name']]
            library_folder_id = galaxy_library.get_library_folder_id(new_dir[1:])
            print "Library Folder", "/" + "/".join(new_dir[1:]), library_folder_id
            file_name = "%s.version_%s" % (res['entity.name'], res['entity.versionLabel'])
            dataset_id = galaxy_library.get_library_dataset_id( library_folder_id, file_name )
            if dataset_id is None:
                try:
                    ent = syn.downloadEntity(res['entity.id'])
                    ann = syn.getAnnotations(ent)
                    meta = dict(ann)
                    del meta['uri']
                    del meta['etag']
                    for c in [ 'platform', 'disease', 'tissueType']:
                        if c in ent:
                            meta[c] = ent[c]
                    print meta
                    if 'cacheDir' in ent:
                        file_path = os.path.join(ent['cacheDir'], ent['files'][0])
                        new_path = os.path.join(ent['cacheDir'], file_name)
                        print file_path, meta
                        os.symlink(file_path, new_path)
                        #paste the file path
                        new_ent = galaxy_library.library_paste_file(library_folder_id, file_name, meta, new_path)
                        #print galaxy_library.item_rename( library_folder_id, new_ent[0]['id'], file_name, res['entity.id'], "Downloaded from https://www.synapse.org/#!Synapse:" + res['entity.id'] )                        
                        #print "File: %s/%s" % ("/".join(cur_path), res['entity.name'])
                except Exception, e:
                    print e
            else:
                print "Found", res['entity.name']
            
        elif res['entity.nodeType'] == 13:
            #skip summaries
            pass
        else:
            print res['entity.name'], res['entity.nodeType']
            
    

def main(api_key, api_url, synapse_project):
    syn = synapseclient.Synapse()
    syn.login()
    
    remote_galaxy = RemoteGalaxy(api_url, api_key)

    ent = syn.getEntity(synapse_project)
    lsync = LibrarySync(remote_galaxy, ent['name'] )
    
    project_scan(syn, synapse_project, lsync)
    


if __name__ == '__main__':
    try:
        api_key = sys.argv[1]
        api_url = sys.argv[2]
        synapse_project = sys.argv[3]
    except IndexError:
        print 'usage: %s key url synapse_folder' % os.path.basename( sys.argv[0] )
        sys.exit( 1 )
    main(api_key, api_url, synapse_project)