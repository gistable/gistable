import os
import sys
import cPickle
import time
import hashlib
import logging
import uuid

import cmemcached

logger =logging.getLogger('tornado session')
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
def LOG(s):
    logger.info(s)

class SessionData():
    def __init__(self, id = None):
        self._data = {}
        self._id = id
        self._is_updated = False
        self._last_time = time.time()
    def get(self,key):
        ret = None
        try:
            ret = self._data[key]
        except:
            pass
        self._last_time = time.time()
        return ret
        
    def set(self, key, value):
        self._data[key] = value
        self._is_updated = True
        self._last_time = time.time()
    
    def get_id(self):
        return self._id
    
    def reset_update_status(self):
        self._is_updated = False
        
    def is_updated(self):
        return self._is_updated
    
class SessionManager():
    def __init__(self, mc_server = ['127.0.0.1:12111']):
        self._mc_data_pool = cmemcached.Client(mc_server)
    
    def write_session_data(self, id, data):
        self._mc_data_pool.set(id,cPickle.dumps(data), 30 * 60)

    def read_session_data(self, id):
        obj = self._mc_data_pool.get(id)
        if obj is None:
            return SessionData(id)
        else:
            return cPickle.loads(obj)

def session(function):
    def _session(*args, **kwargs):
        self = args[0]
        if not self.get_secure_cookie("sessionid"):
            LOG('no session')
            newid = hashlib.md5(str(uuid.uuid1())).hexdigest()
            sessionid = newid
            self.set_secure_cookie("sessionid", sessionid)
        else:
            sessionid = self.get_secure_cookie("sessionid")
        obj = session_manager.read_session_data(sessionid)
        LOG('SESSIONID:' + sessionid)
        self.session = obj
        self.session.reset_update_status()
        res = function(*args, **kwargs)
        if self.session.is_updated():
            LOG('session update' + ' ' + sessionid)
            session_manager.write_session_data(sessionid, self.session)
        else:
            LOG('no session operation')
            pass
        return res
    return _session

session_manager = SessionManager()