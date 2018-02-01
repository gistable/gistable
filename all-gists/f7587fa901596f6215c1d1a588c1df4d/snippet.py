#!/usr/bin/env python

# Install fake factory at first. Helps us create 50k customers in odoo
# pip install fake-factory
# Documentation for odoo is listed here
# https://www.odoo.com/documentation/9.0/api_integration.html#calling-methods

# MIT License

# Copyright (c) 2016 Jasim Muhammed

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import xmlrpclib
from faker import Factory as FakeFactory

from random import choice


# Server settings
proto = 'http'
host = '127.0.0.1'
port = '8069'

db = 'odoo_test'


# Acess details
username = 'test123@mailinator.com'
password = '123456'

# Defaults
COUNTRY_USA_ID = 235
CITY_FLORIDA_ID = 10
COMPANY_ID_DEFAULT = 1

# Fake generation factory
fake_gen = FakeFactory.create()


def get_rpc_url(path):
    """
    Generate XML RPC URL for the endpoint
    :param path: default is object
    """
    return '{}://{}:{}/xmlrpc/2/{}'.format(proto, host, port, path)


def login():
    common = xmlrpclib.ServerProxy(get_rpc_url('common'))
    uid = common.authenticate(db, username, password, {})
    return uid


def insert_customers(uid, num=1):
    """
    Generate large number of payloads
    :param num: number of contact payloads to generate
    """
    users = []

    def street():
        return choice([
            'Auburndale, Auburndale Chamber Main Street',
            'Avon Park, Avon Park Main Street',
            'Bartow, Downtown Bartow Inc',
            'Blountstown, Blountstown Chamber of Comm',
            'Clearwater, Clearwater Main Street',
            'Cocoa, Cocoa Main Street'
        ])
    models = xmlrpclib.ServerProxy(get_rpc_url('object'))
    for i in range(num):
        payload = []
        street2, street1 = street().split(',')
        name = fake_gen.name()
        payload.append(
            {
                'name': name,
                'is_company': False,
                'customer': True,
                "street": street1,
                "street2": street2,
                "city": "Test City Florida",
                "state_id": CITY_FLORIDA_ID,
                "company_id": COMPANY_ID_DEFAULT,
                "country_id": COUNTRY_USA_ID}
        )

        user = models.execute_kw(
            db, uid, password,
            'res.partner', 'create',
            payload
        )
        users.append(user)
        print "{}:{}".format(user, name)
    return users

# Get user id the account
uid = login()
users = insert_customers(uid, num=50000)
print users
