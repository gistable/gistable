#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2
import json

# Linode API Key
key = 'API_KEY'
# set your VPS root password
root_pass = 'AWESOME_PASSWORD'
# stackscript id, see from its url
stack_script_id = 1234


def buy():
    buy_url = 'https://api.linode.com/?api_key=%s&api_action=linode.create&DatacenterID=2&PlanID=1&PaymentTerm=1' % (key)
    f = urllib2.urlopen(buy_url)
    result = json.load(f)
    print result
    return result['DATA']['LinodeID']

def config(linode_id, diskid):
    config_url = 'https://api.linode.com/?api_key=%s&api_action=linode.config.create&label=myprofile&LinodeID=%s&KernelID=138&disklist=%s,,,,,,,,' % (key, linode_id, diskid)
    f = urllib2.urlopen(config_url)
    result = json.load(f)
    print result
    
def create_swap_disk(linode_id):
    disk_url = 'https://api.linode.com/?api_key=%s&api_action=linode.disk.create&LinodeID=%s&label=swap&size=256&type=swap' % (key, linode_id)
    f = urllib2.urlopen(disk_url)
    result = json.load(f)
    print result

def create_disk(linode_id):
    disk_url = 'https://api.linode.com/?api_key=%s&api_action=linode.disk.createfromstackscript&LinodeID=%s&StackScriptID=%s&StackScriptUDFResponses={}&DistributionID=109&label=debian&size=48896&rootPass=%s' % (key, linode_id, stack_script_id, root_pass)
    f = urllib2.urlopen(disk_url)
    result = json.load(f)
    print result
    return result['DATA']['DiskID']
    
def boot(linode_id):
    boot_url = 'https://api.linode.com/?api_key=%s&api_action=linode.boot&linodeID=%s' % (key, linode_id)
    f = urllib2.urlopen(boot_url)
    result = json.load(f)
    print result
     
def update_group(linode_id):
    boot_url = 'https://api.linode.com/?api_key=%s&api_action=linode.update&linodeID=%s&lpm_displayGroup=miner' % (key, linode_id)
    f = urllib2.urlopen(boot_url)
    result = json.load(f)
    print result
    
def all():
    linode_id = buy()
    disk_id = create_disk(linode_id)
    create_swap_disk(linode_id)
    config(linode_id, disk_id)
    boot(linode_id)
    update_group(linode_id)
    
for i in xrange(0, 100):
    all()
