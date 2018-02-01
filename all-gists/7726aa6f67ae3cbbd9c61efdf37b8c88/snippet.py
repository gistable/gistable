#!/usr/bin/python

""" Ansible Inventory Generated From Netbox

Author: Stanley Karunditu <stanley@linuxsimba.com>

License: MIT

Requirements:
* use netbox device roles that result in hyphenated role names. E.g
  linux-switch, openstack-linux-server. The script takes the string and splits
  it at the "-". So for a "linux-switch" role the device is put in the [linux]
  and [switch] inventory groups
* Assign the NETBOX_USERNAME, NETBOX_PASSWD, NETBOX_URL and PXE_SERVER settings
  in your bash environmental variables. The script will read this output and
  use it to create the dynamic inventory.
"""

import argparse
import sys
import requests
from requests.auth import HTTPBasicAuth
import json
import re
import os

# Get netbox settings from shell environment variables
try:
    USERNAME = os.environ['NETBOX_USER']
    PASSWORD = os.environ['NETBOX_PASSWD']
    NETBOX_URL = os.environ['NETBOX_URL']
    PXE_SERVER = os.environ['PXE_SERVER']
except KeyError as e:
    print("Failed to get netbox settings from shell environment var %s" % (e))
    exit(1)

# Keeps track of PXE Hosts
# Format: [ { "name": hosta,
#             "ip": "a.b.c.d/21",
#             "mac_addresses": ["mac1", "macb"]}]
PXE_HOST_HASH = []

INVENTORY_GROUPS = {}


def api_call(url):
    """ Return the Output an API Call

    """
    api_url = "%s/%s" % (NETBOX_URL, url)
    response = requests.get(api_url,
                            auth=HTTPBasicAuth(USERNAME, PASSWORD))
    # Exit with a HTTPError if status_code is not 200.
    response.raise_for_status()
    return response.json()


def device_list():
    """ Return Raw Data from /api/dcim/devices API call

    Args: None
    Returns:
        dict: full device list
    Todo:
        Restrict Device output per tenant so its not so big.
    """
    return api_call("api/dcim/devices")


def device_interfaces(device_id):
    """ Return raw list of interfaces associated with a particular device
    Args:
        device_id(int): ID of a particular device
    Returns:
        dict: list of interfaces associated with a particular device
    """
    return api_call("api/dcim/devices/%s/interfaces" % (device_id))


def device_nic_ips(device_id):
    """ Return the list of interfaces
    Args:
        device_id(int): ID of a particular device
    Returns:
        dict: list of ip address associated with a particular device
    """
    return api_call("api/ipam/ip-addresses/?device_id=%s" % (device_id))


def list_full_inventory():
    """ Return full list of inventory
    Activated when --list is used on this program
    Args:
        None
    Return:
        str: JSON Hash of inventory from netbox in a Ansible inventory format
    """
    # Initialize Final Ansible Hash
    inventory_hash = {}
    # Get the list of all interdevice connections
    for device in device_list():
        _name = device['name']
        inventory_hash[_name] = create_device_inventory_entry(device)
    # add entry for pxe host
    # pxeserver {
    #   'hosts: [1.1.1.1],
    #   'vars': { 'pxe_hosts': { PXE_HOST_HASH data }
    # }
    inventory_hash['pxeserver'] = {
        'host': [PXE_SERVER],
        'vars': {
            'pxe_hosts': PXE_HOST_HASH
        }
    }
    inv_groups = INVENTORY_GROUPS.copy()
    inventory_hash.update(inv_groups)
    return inventory_hash


def create_device_inventory_entry(device):
    """Create Ansible Inventory JSON entry for a single device

    Example::
        "r1-b1": {
          "hosts": ["172.17.100.1"],
          "vars": {
            "primary_ip_addr": "172.17.100.1",
            "primary_ip_prefix": "24",
            "interfaces" {
              "ipmi0": {
                mac: "AA:BB:CC:DD:EE:FF"
                ip: "X.Y.Z.A/25"
              }
              "eno0": {
                mac: "BB:CC:DD:EE:FF:DD"
                ip: "X.Y.D.B/21"
              }
            }
          }
        }
    Args:
        device(dict): Dict containing the device data
    Return:
        str: JSON hash for the device
    """
    json_hash = {"hosts": [], "vars": {"interfaces": {}}}
    _vars = json_hash['vars']
    primary_ip = device_primary_ip(device)
    _vars['interfaces'] = device_nics(device)
    _vars['primary_ip_addr'] = ''
    _vars['primary_ip_prefix'] = ''
    if primary_ip:
        json_hash['hosts'].append(primary_ip['address'])
        _vars['primary_ip_addr'] = primary_ip['address']
        _vars['primary_ip_prefix'] = primary_ip['prefix']
    set_inventory_groups(device)
    return json_hash


def set_inventory_groups(device):
    """ add device to various inventory groups as defined in the device
    role attribute
    Args:
        device(dict): Device name
    Returns:
        None
    """
    device_role = device.get('device_role')
    if not device_role:
        return

    inventory_groups = device.get('device_role').get('slug').split('-')
    for _group in inventory_groups:
        if not INVENTORY_GROUPS.get(_group):
            INVENTORY_GROUPS[_group] = {'children': []}
        INVENTORY_GROUPS.get(_group).get('children').append(device.get('name'))


def device_nics(device):
    """Get Nic details for a particular device
    Args:
        device(dict): Device details
    Return:
        dict: First and IPMI details. If a switch return blank. Example::
            {
             "ipmi": { "ip": X.X.X.X, "prefix": "26" }
            }
    """
    # check if a device role is assigned. if not return blank dict
    if not device.get('device_role'):
        return {}
    # check if the entry is a switch, if so, don't list any ports
    if re.search('switch', device['device_role']['slug']):
        return {}
    output = {}
    device_id = device['id']
    nic_ips = device_nic_ips(device_id)
    nic_ips_dict = {i['interface']['id']: i for i in nic_ips}
    pxe_macs = []
    for _nic in device_interfaces(device_id):
        _nic_id = _nic['id']
        _nic_ip = ""
        if nic_ips_dict.get(_nic_id):
            _nic_ip = nic_ips_dict[_nic_id]['address']
        _mac_address = _nic['mac_address']
        if _nic['name'].startswith('ipmi'):
            output['ipmi'] = {'mac': "", 'ip': _nic_ip}
        elif _nic['form_factor'] != 'Virtual':
            _name = _nic['name']
            output[_name] = {'mac': _mac_address, 'ip': _nic_ip}
            pxe_macs.append(_mac_address)

    add_pxe_entry(pxe_macs, device)
    return output


def add_pxe_entry(pxe_macs, device):
    """ add entries to the pxe host hash
    Args:
        pxe_macs(list): list of macs that can be used to pxe the host
        device(dict): basic info about the device from netbox
    Returns
        None
    """
    pxe_entry = {'name': device['name'], 'mac_addresses': pxe_macs}
    if device.get('primary_ip4'):
        pxe_entry['ip'] = device.get('primary_ip4').get('address')
    else:
        pxe_entry['ip'] = ""
    PXE_HOST_HASH.append(pxe_entry)


def device_primary_ip(device):
    """ Get primary IP of Device if it is available
    Assumes it is IPv4 , for now.
    Args:
        device(dict): Dict containing device info
    Returns:
        dict: primary ip and prefix info if available. Otherwise return None
    """
    primary_ip = device['primary_ip']
    if primary_ip:
        full_ip = primary_ip['address'].split('/')
        return {'address': full_ip[0], 'prefix': full_ip[1]}

    return primary_ip


def create_inventory(_args):
    """ Creates the JSON ansible inventory
    Args:
        _args (dict): Parameters from argparse
    Return:
        str:  The return value is a JSON hash.
    """
    if _args.list is None:
        return "{}"
    else:
        return list_full_inventory()


def print_help(parser):
    parser.print_help()
    exit(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Generate Ansible Inventory from Netbox")
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--list', action='store_true')
    group.add_argument('--host', type=str)
    if (len(sys.argv) < 2):
        print_help(parser)
    _args = parser.parse_args()
    print(json.dumps(create_inventory(_args)))
