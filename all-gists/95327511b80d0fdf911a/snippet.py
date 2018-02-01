#!/usr/bin/env python
# encoding: utf-8
"""
digitalocean
Created by Djordje Stojanovic <djordje.stojanovic@shadow-inc.net>

Based on DigitalOcean inventory plugin:
https://raw.githubusercontent.com/ansible/ansible/devel/plugins/inventory/digital_ocean.py
"""

import os
import sys
import re
from operator import itemgetter
try:
	import json
except ImportError:
	import simplejson as json
try:
	from cement.core import foundation, controller, handler, hook
except ImportError:
	print "failed=True msg='`cement` library required. Install with `sudo pip install cement`'"
	sys.exit(1)
try:
	from dopy.manager import DoError, DoManager
except ImportError:
	print "failed=True msg='`dopy` library required. Install with `sudo pip install dopy`'"
	sys.exit(1)
	
app_name = 'digitalocean'
token = None
manager = None

class AnsibleInventory(object):
	def __init__(self, data):
		self.fqdn_validator = re.compile(r'(?=^.{4,255}$)(^((?!-)[a-zA-Z0-9-]{0,62}[a-zA-Z0-9]\.)+[a-zA-Z]{2,63}$)')
		self.data = data
		self._parse()
	
	def _parse(self):
		self.inventory = dict()
	
	def add_host(self, group, hostname, ip_address='', variables={}):
		group not in self.inventory and self.inventory.update({ group: { 'hosts': [] } })
		self.inventory[group]['hosts'].extend([hostname])
		variables is not {} and self.set_host_variable(hostname, variables)
		if ip_address is not '' and not self.is_fqdn(hostname):
			self.set_host_variable(hostname, 'ansible_ssh_host', ip_address)
	
	def set_host_variable(self, hostname, variable, value=''):
		if type(variable) is dict:
			self.set_meta('hostvars', { hostname: variable })
		else:
			self.set_meta('hostvars', { hostname: { variable: value } })
	
	def get_host_variable(self, hostname, variable):
		if '_meta' in self.inventory and 'hostvars' in self.inventory['_meta'] and hostname in self.inventory['_meta']['hostvars'] and variable in self.inventory['_meta']['hostvars'][hostname]:
			return self.inventory['_meta']['hostvars'][hostname][variable]
		else:
			return None
	
	def get_host_variables(self, hostname):
		if '_meta' in self.inventory and 'hostvars' in self.inventory['_meta'] and hostname in self.inventory['_meta']['hostvars']:
			return self.inventory['_meta']['hostvars'][hostname]
		else:
			return None
	
	def set_group_variable(self, group, variable, value):
		group not in self.inventory and self.inventory.update({ group: { 'hosts': [], 'vars': {} } })
		if type(variable) is dict:
			self.inventory[group]['vars'].update(value)
		else:
			self.inventory[group]['vars'][variable] = value
	
	def get_group_variable(self, group, variable):
		if group in self.inventory and 'vars' in self.inventory[group] and variable in self.inventory[group]['vars']:
			return self.inventory[group]['vars'][variable]
		else:
			return None
	
	def set_meta(self, variable, value):
		'_meta' not in self.inventory and self.inventory.update({ '_meta': {} })
		variable not in self.inventory['_meta'] and self.inventory['_meta'].update({ variable: {} })
		self.inventory['_meta'][variable].update(value)
	
	def is_fqdn(self, hostname):
		hostname = hostname.encode('idna').lower()
		return bool(self.fqdn_validator.match(hostname))
	
	def to_json(self, indent=2, sort_keys=True):
		return json.dumps(self.inventory, indent=indent, sort_keys=sort_keys)
	
	def to_inventory(self):
		pass
	
class DigitalOceanInventory(AnsibleInventory):
	def __init__(self, data, group_by=['region', 'image', 'size', 'status']):
		self.group_by = group_by
		self.hostvars = ['hostname', 'eth'] + self.group_by
		super(DigitalOceanInventory, self).__init__(data)
	
	def _parse(self):
		super(DigitalOceanInventory, self)._parse()
		self.meta = self._extract_meta()
		for droplet in self.meta:
			self.add_droplet(droplet)
		
	def _extract_meta(self):
		filter_network_by_type = lambda network_type, network_data: filter(lambda network: network['type'] == network_type, network_data)
		meta = []
		for droplet in self.data:
			final_form = {
				'hostname': str(droplet['name']),
				'size': str(droplet['size_slug']),
				'region': str(droplet['region']['slug']),
				'image': str(droplet['image']['slug']),
				'eth': {},
				'status': str(droplet['status'])
			}
			public_networks = filter_network_by_type('public', droplet['networks']['v4'])
			private_networks = filter_network_by_type('private', droplet['networks']['v4'])
			len(public_networks) > 0 and final_form['eth'].update({'public': {'ip': str(public_networks[0]['ip_address'])}})
			len(private_networks) > 0 and final_form['eth'].update({'private': {'ip': str(private_networks[0]['ip_address'])}})
			meta.append(final_form)
		meta = sorted(meta, key=itemgetter('hostname'))
		return meta
		
	def add_droplet(self, droplet):
		'droplets' not in self.inventory and self.inventory.update({ 'droplets': { 'hosts': [] } })
		self.inventory['droplets']['hosts'].extend([droplet['hostname']])
		filter_keys = lambda dictionary, keys: dict([ (i, dictionary[i]) for i in dictionary if i in keys])
		for group in self.group_by:
			key = group+'_'+droplet[group]
			key not in self.inventory and self.inventory.update({ key: { 'hosts': [] } })
			self.inventory[key]['hosts'].extend([droplet['hostname']])
		self.set_host_variable(droplet['hostname'], filter_keys(droplet, self.hostvars))
		if not self.is_fqdn(droplet['hostname']):
			self.set_host_variable(droplet['hostname'], 'ansible_ssh_host', droplet['eth']['public']['ip'])

class ApiController(controller.CementBaseController):
	class Meta:
		label = 'api'
		arguments = [
			(['--api-token', '-a'], dict(action='store', metavar='API_TOKEN', help='Set DigitalOcean API Token')),
			(['--env'], dict(action='store_true', help='Export environment variables from config'))
		]

class AnsibleController(controller.CementBaseController):
	class Meta:
		# label = 'ansible'
		description = 'Ansible Dynamic Inventory'
		arguments = [
			(['--list'], dict(action='store_true', help='Lists Ansible inventory')),
			(['--host'], dict(action='store', metavar='HOSTNAME', help='Return variables for hostname')),
		]

	@controller.expose(hide=True, aliases=['run'])
	def default(self):
		if self.app.pargs.list:
			if manager:
				data = manager.all_active_droplets()
				print (not len(data) and data) or DigitalOceanInventory(data).to_json()
		elif self.app.pargs.host:
			if manager:
				data = manager.all_active_droplets()
				if len(data):
					print json.dumps(DigitalOceanInventory(data).get_host_variables(self.app.pargs.host), indent=2)
				else:
					print json.dumps({})
		elif self.app.pargs.env:
			print 'DO_API_TOKEN='+token

class DigitalOceanApp(foundation.CementApp):
	class Meta:
		label = app_name
		description = 'DigitalOcean CLI'
		base_controller = AnsibleController

def token_check_hook(app):
	global token
	token = app.pargs.api_token or os.getenv('DO_API_TOKEN')
	if not token and (app.config.has_section(app_name) and 'api_token' in app.config.keys(app_name)):
		token = app.config.get(app_name, 'api_token')
	elif not token:
		print '''Specify your DigitalOcean API Token:
		* in your config file ($HOME/.'''+app_name+'''/config)
		ex.

		[digitalocean]
		api_token = 0000000000000000000000000000000000000000000000000000000000000000

		* environment variable `DO_API_TOKEN`
		* using the flag --api-token/-a API_TOKEN'''
		sys.exit(1)

def setup_manager_hook(app):
	global manager
	manager = DoManager(None, token, api_version=2)

def main():
	app = DigitalOceanApp()
	handler.register(ApiController)
	hook.register('post_argument_parsing', token_check_hook, weight=0)
	hook.register('post_argument_parsing', setup_manager_hook, weight=1)
	try:
		app.setup()
		app.run()
	finally:
		app.close()
	
if __name__ == '__main__':
	main()