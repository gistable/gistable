import logging
import grequests as async
import requests
import json as js

prefix = "large_new_compose"

def request_json(prefix, i):
    return js.dumps({
        "organization_id": 1,
        "name": "host_{0}_{1}".format(prefix, i),
        "type": "system",
        "content_view_id": "1",
        "facts": {"uname.machine": "unknown"}})

logging.basicConfig(filename='spamming_{0}.log'.format(prefix), level=logging.DEBUG)


def print_res(r, *args, **kwargs):
    logging.info("Recieved: {0}, {1}".format(r.status_code, r.content))

async_list = []

def spam():
    for i in range(1, 90):
        json = request_json(prefix, i)
        item = async.request(
            method='post',
            headers={
                'content-type': 'application/json',
                "Accept": "application/json,version=2"},
            verify=False,
            url='https://qetello02.usersys.redhat.com/katello/api/environments/1/systems/',
            auth=('admin', 'changeme'),
            data=json,
            hooks=dict(response=print_res))
        logging.info("Sent: {0}".format(json))
        async_list.append(item)
    async.map(async_list)
