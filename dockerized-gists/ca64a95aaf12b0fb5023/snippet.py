#!/usr/bin/env python
# Name:     cloudscan.py
# Purpose:  Run Nessus Cloud Scans Easily. 
# By:       Jerry Gamblin
# Date:     11.05.15
# Modified  11.05.15
# Rev Level 0.5
# -----------------------------------------------

import requests
import json
import time
import sys
import os
from urllib2 import urlopen


def color(text, color_code):
    if sys.platform == "win32" and os.getenv("TERM") != "xterm":
        return text

    return '\x1b[%dm%s\x1b[0m' % (color_code, text)


def red(text):
    return color(text, 31)

def blue(text):
    return color(text, 34)

url = 'https://us-2a.svc.nessus.org'
verify = True
token = ''
username = ''
password = ''


def build_url(resource):
    return '{0}{1}'.format(url, resource)


def connect(method, resource, data=None, params=None):
    """
    Send a request

    Send a request to Nessus based on the specified data. If the session token
    is available add it to the request. Specify the content type as JSON and
    convert the data to JSON format.
    """
    headers = {'X-Cookie': 'token={0}'.format(token),
               'content-type': 'application/json'}

    data = json.dumps(data)

    if method == 'POST':
        r = requests.post(build_url(resource), data=data, headers=headers, verify=verify)
    elif method == 'PUT':
        r = requests.put(build_url(resource), data=data, headers=headers, verify=verify)
    elif method == 'DELETE':
        r = requests.delete(build_url(resource), data=data, headers=headers, verify=verify)
    else:
        r = requests.get(build_url(resource), params=params, headers=headers, verify=verify)

    # Exit if there is an error.
    if r.status_code != 200:
        e = r.json()
        print e['error']
        sys.exit()

    # When downloading a scan we need the raw contents not the JSON data. 
    if 'download' in resource:
        return r.content

    # All other responses should be JSON data. Return raw content if they are
    # not.
    try:
        return r.json()
    except ValueError:
        return r.content


def login(usr, pwd):
    """
    Login to nessus.
    """

    login = {'username': usr, 'password': pwd}
    data = connect('POST', '/session', data=login)

    return data['token']


def logout():
    """
    Logout of nessus.
    """

    connect('DELETE', '/session')


def get_policies():
    """
    Get scan policies

    Get all of the scan policies but return only the title and the uuid of
    each policy.
    """

    data = connect('GET', '/editor/policy/templates')

    return dict((p['title'], p['uuid']) for p in data['templates'])


def get_history_ids(sid):
    """
    Get history ids

    Create a dictionary of scan uuids and history ids so we can lookup the
    history id by uuid.
    """
    data = connect('GET', '/scans/{0}'.format(sid))

    return dict((h['uuid'], h['history_id']) for h in data['history'])


def get_scan_history(sid, hid):
    """
    Scan history details

    Get the details of a particular run of a scan.
    """
    params = {'history_id': hid}
    data = connect('GET', '/scans/{0}'.format(sid), params)

    return data['info']


def add(name, desc, targets, pid):
    """
    Add a new scan

    Create a new scan using the policy_id, name, description and targets. The
    scan will be created in the default folder for the user. Return the id of
    the newly created scan.
    """

    scan = {'uuid': pid,
            'settings': {
                'name': name,
                'description': desc,
                'text_targets': targets}
            }

    data = connect('POST', '/scans', data=scan)

    return data['scan']


def update(scan_id, name, desc, targets, pid=None):
    """
    Update a scan

    Update the name, description, targets, or policy of the specified scan. If
    the name and description are not set, then the policy name and description
    will be set to None after the update. In addition the targets value must
    be set or you will get an "Invalid 'targets' field" error.
    """

    scan = {}
    scan['settings'] = {}
    scan['settings']['name'] = name
    scan['settings']['desc'] = desc
    scan['settings']['text_targets'] = targets

    if pid is not None:
        scan['uuid'] = pid

    data = connect('PUT', '/scans/{0}'.format(scan_id), data=scan)

    return data


def launch(sid):
    """
    Launch a scan

    Launch the scan specified by the sid.
    """

    data = connect('POST', '/scans/{0}/launch'.format(sid))

    return data['scan_uuid']


def status(sid, hid):
    """
    Check the status of a scan run

    Get the historical information for the particular scan and hid. Return
    the status if available. If not return unknown.
    """ 

    d = get_scan_history(sid, hid)
    return d['status']


def export_status(sid, fid):
    """
    Check export status

    Check to see if the export is ready for download.
    """

    data = connect('GET', '/scans/{0}/export/{1}/status'.format(sid, fid))

    return data['status'] == 'ready'


def export(sid, hid):
    """
    Make an export request

    Request an export of the scan results for the specified scan and
    historical run. In this case the format is hard coded as nessus but the
    format can be any one of nessus, html, pdf, csv, or db. Once the request
    is made, we have to wait for the export to be ready.
    """

    data = {'history_id': hid,
            'format': 'pdf',
            'chapters': 'vuln_hosts_summary'}

    data = connect('POST', '/scans/{0}/export'.format(sid), data=data)

    fid = data['file']

    while export_status(sid, fid) is False:
        time.sleep(5)

    return fid


def download(sid, fid):
    """
    Download the scan results

    Download the scan results stored in the export file specified by fid for
    the scan specified by sid.
    """

    data = connect('GET', '/scans/{0}/export/{1}/download'.format(sid, fid))
    filename = 'nessus_{0}_{1}.pdf'.format(sid, fid)

    print('Saving scan results to {0}.'.format(filename))
    with open(filename, 'w') as f:
        f.write(data)
    os.system("open " +filename) 
    #os.system("Start " +filename) < If you are doing this on Windows for some reason.

def delete(sid):
    """
    Delete a scan

    This deletes a scan and all of its associated history. The scan is not
    moved to the trash folder, it is deleted.
    """

    connect('DELETE', '/scans/{0}'.format(scan_id))


def history_delete(sid, hid):
    """
    Delete a historical scan.

    This deletes a particular run of the scan and not the scan itself. the
    scan run is defined by the history id.
    """

    connect('DELETE', '/scans/{0}/history/{1}'.format(sid, hid))


if __name__ == '__main__':

    my_ip = urlopen('http://ip.42.pl/raw').read()

    print(blue('A quick script to run nessus cloud scans by @jgamblin but mostly stolen from @averagesecguy'))
    
    print('\n')
    print(red('Your public IP address is {0}'.format(my_ip)))
    print('\n')

    #Get IP To SCAN

    resp = raw_input(blue('Would you like to scan {0}? (Y/N):'.format(my_ip)))

    if resp.lower() in ["yes", "y"]:
        ip = my_ip
    else:
        ip = raw_input(blue("What would you like to scan?: "))

    name = raw_input(blue("What would you like to name this scan? "))

    q1=input(blue("\nScan Types: \n1. Host Discovery Scan\n2. Basic Network Scan\n3. Web Application Tests:\nWhich one do you want to run?:")) 

    if q1 == 1:
        policytype = ("Host Discovery")
    elif q1 == 2:
        policytype = ("Basic Network Scan")
    elif q1 == 3:
        policytype = ("Web Application Tests")
    else:
        print("\nUm...that wasnt a choice.")

    print('\n')

    print('Login')
    token = login(username, password)

    print('Adding new scan.')
    policies = get_policies()
    policy_id = policies[policytype]
    scan_data = add(name, 'Create a new scan with API', ip , policy_id) 
    scan_id = scan_data['id']

    print('Updating scan with new targets.')
    update(scan_id, scan_data['name'], scan_data['description'], ip)

    print('Launching new scan.')
    scan_uuid = launch(scan_id)
    history_ids = get_history_ids(scan_id)
    history_id = history_ids[scan_uuid]
    while status(scan_id, history_id) != 'completed':
        time.sleep(5)

    print('Exporting the completed scan.')
    file_id = export(scan_id, history_id)
    download(scan_id, file_id)

    print('Deleting the scan.')
    history_delete(scan_id, history_id)
    delete(scan_id)

    print('Logout')
    logout()
