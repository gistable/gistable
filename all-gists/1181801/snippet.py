#!/usr/bin/env python
#-*- coding: utf-8 -*-
import xmlrpclib


class OpenERPAPI(object):
    URL = 'http://your_server:8069/xmlrpc'
    USER = 'your_user'
    PWD = 'your_passoword'
    DBNAME = 'your_dbname'
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(OpenERPAPI, cls).__new__(cls, *args, **kwargs)
            cls._instance.config_run()
        return cls._instance

    def config_run(self):
        sock_common = xmlrpclib.ServerProxy(self.URL + '/common')
        self.uid = sock_common.login(self.DBNAME, self.USER, self.PWD)
        self.sock = xmlrpclib.ServerProxy(self.URL + '/object')

    def execute(self, erpobj, method, *args, **kwargs):
        data = self.sock.execute(self.DBNAME, self.uid, self.PWD,
                                erpobj, method, *args, **kwargs)
        return data
API = OpenERPAPI()


class OpenERPObject(object):

    def __init__(self, erp_name):
        self.erp_name = erp_name

    def __getattr__(self, name):
        def remote_method(*args, **kwargs):
            return API.execute(self.erp_name, name, *args, **kwargs)
        return remote_method


if __name__ == '__main__':
    e = OpenERPObject('hr.employee')
    ids = e.search([('id', '=', 1)])
    print e.read(ids, ['name'])
    ids = e.search([])
    print e.read(ids, ['name'])

    t = OpenERPObject('hr_timesheet_sheet.sheet')
    print t.sign_in([1])
    import time
    time.sleep(3)
    print t.sign_out([1])

    c = OpenERPObject('hr.contract')
    ids = c.search([])
    print c.read(ids)