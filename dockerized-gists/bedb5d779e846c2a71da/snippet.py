#!/usr/bin/python
import json
import os
from flask import Flask
from ConfigParser import ConfigParser
app = Flask(__name__)

LOGICAL_DIR = "{{ vault_backend_path}}/logical/"
VAULT_URL = "https://{{ vault_default_cert_url }}:{{ vault_default_port }}"

def recursive(array):
    keys_list = ''
    for key in array:
        if 'customer' not in key:
            if key[:1] == "_":
                keys_list += '<li>%s</li>' % key[1:]
            else:
                keys_list += '<li>%s<ul>' % key + recursive(array[key]) + '</ul></li>'
    return keys_list


def explore(rootdir):
    """
    Creates a nested dictionary that represents the folder structure of rootdir
    """
    html = "<html><body><table border=1>"

    dir = {}
    rootdir = rootdir.rstrip(os.sep)
    start = rootdir.rfind(os.sep) + 1
    for path, dirs, files in os.walk(rootdir):
        folders = path[start:].split(os.sep)
        subdir = dict.fromkeys(files)
        parent = reduce(dict.get, folders[:-1], dir)
        parent[folders[-1]] = subdir

    html += "<tr><td><b>Customer</b></td><td><b>Keys</b></td></tr>"
    for customer in dir['logical']:
        keys_list = ''
        customer_name = "noname"
        # find customer name
        for key in dir['logical'][customer]:
            if 'customer' in key:
                customer_name = key.split('_customer')[0][1:]
        keys_list += (recursive(dir['logical'][customer]))
        html += "<tr><td>" + customer_name + "</td>"
        html += "<td><ul>" + keys_list + "</ul></td>"
        html += "</tr>"
    html += "</table></body></html>"
    return html

@app.route('/')
def list_index():
    return explore(LOGICAL_DIR)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)