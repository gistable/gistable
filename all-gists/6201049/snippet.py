#!/usr/bin/env python
# -*- coding: utf-8 -*-
# prerequisites :
# 	sudo apt-get install nmap
#
#  nmap.py
#  Network Radar
#  
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  
# Author: Emad Elsaid a.k.a Blaze Boy
# Email: blazeebot[at]gmail[dot]com
# URL: [www|facebook|youtube|twitter|linkedin|github].blazeboy.me

import os, gtk, gobject, time, appindicator, subprocess, time, pynotify, threading
gobject.threads_init()

bits_raw = """32 255.255.255.255
31 255.255.255.254
30 255.255.255.252
29 255.255.255.248
28 255.255.255.240
27 255.255.255.224
26 255.255.255.192
25 255.255.255.128
24 255.255.255.0
23 255.255.254.0
22 255.255.252.0
21 255.255.248.0
20 255.255.240.0
19 255.255.224.0
18 255.255.192.0
17 255.255.128.0
16 255.255.0.0
15 255.254.0.0
14 255.252.0.0
13 255.248.0.0
12 255.240.0.0
11 255.224.0.0
10 255.192.0.0
9 255.128.0.0
8 255.0.0.0
7 254.0.0.0
6 252.0.0.0
5 248.0.0.0
4 240.0.0.0
3 224.0.0.0
2 192.0.0.0
1 128.0.0.0
0 0.0.0.0"""
bits = {}
for bit in bits_raw.split("\n"):
	v,k = bit.split(" ")
	bits[k] = v
		
show_notifications = True
def switch_show_notifications(checkmenuitem):
	global show_notifications
	show_notifications = checkmenuitem.get_active()
	
hosts_notifier_ar = []
def hosts_notifier(hosts):
	global hosts_notifier_ar
	new_hosts = []
	disconnected_hosts = []
	for host in hosts:
		if not host in hosts_notifier_ar:
			new_hosts.append(host)
			
	hosts_notifier_ar += new_hosts
	
	for host in hosts_notifier_ar:
		if not host in hosts:
			disconnected_hosts.append(host)
	
	for host in disconnected_hosts:		
		hosts_notifier_ar.remove(host)
	
	if show_notifications:
		notification_message = ""
		if len(new_hosts)==1:
			notification_message += "One new device joined network ("+new_hosts[0]+")\n"
		elif len(new_hosts)>1:
			notification_message += str(len(new_hosts))+" New devices joined network\n"
			
		if len(disconnected_hosts)==1:
			notification_message += "One device disconnected from network ("+disconnected_hosts[0]+")\n"
		elif len(disconnected_hosts)>1:
			notification_message += str(len(disconnected_hosts))+" Devices disconnected from network\n"
		
		if notification_message!="":
			n = pynotify.Notification("Nadar", notification_message.strip())
			helper = gtk.Button()
			icon = helper.render_icon(gtk.STOCK_NETWORK, gtk.ICON_SIZE_DIALOG)
			n.set_icon_from_pixbuf(icon)
			n.show()
			

def get_interfaces():
	# ifconfig -s
	ifconfig = subprocess.check_output(['ifconfig','-s'])
	devices = []
	for line in ifconfig.split("\n")[1:-1]:
		device = line.split(" ")[0]
		if device!="lo": # add al interfaces except loopback
			devices.append(device)
	return devices
	
def get_ip_mask(device):
	# ifconfig eth0
	ifconfig = subprocess.check_output(['ifconfig', device])
	for line in ifconfig.split("\n"):
		current_line = line.strip()
		if current_line.startswith('inet addr'):
			components = [x for x in current_line.strip().split('  ') if len(x)>0]
			ip_address = components[0].split(':')[1]
			subnet_mask = components[2].split(':')[1]
			if bits.has_key(subnet_mask):
				return (ip_address,bits[subnet_mask])
	return False

def get_default_gateways():
	#  nm-tool | grep Gateway | awk '{print $2}'
	#  man, i love that line :D it feels like magic
	return [ x.strip().split(" ")[-1] for x in subprocess.check_output('nm-tool').split("\n") if x.find("Gateway")>-1 ]

def get_hosts(device):
	# nmap -sn ip/bits
	try:
		ip_mask = get_ip_mask(device)
		arp_scan = subprocess.check_output(['nmap', '-sn', ip_mask[0]+'/'+ip_mask[1]])
		gateways = get_default_gateways()
		hosts = []
		for line in arp_scan.split("\n"):
			# filter lines to the ip lines only
			if line.startswith('Nmap scan report for '):
				host = line[line.rfind(' ')+1:]
				# don't add current machine ip address and don't add gateways
				if host!=ip_mask[0] and not host in gateways:
					hosts.append(host)
		return hosts
	except Exception as e:
		return []

def control_menu_items(menu_obj):
	separator = gtk.SeparatorMenuItem()
	menu_obj.append(separator)
	separator.show()
	
	show_notifications_menuitem = gtk.CheckMenuItem("Show notifications")
	show_notifications_menuitem.set_active(show_notifications)
	show_notifications_menuitem.connect('toggled', switch_show_notifications)
	menu_obj.append(show_notifications_menuitem)
	show_notifications_menuitem.show()
	
	quit_item = gtk.MenuItem("Exit")
	quit_item.connect('activate', gtk.main_quit)
	menu_obj.append(quit_item)
	quit_item.show()


class Refresh_menu(threading.Thread):
	def __init__(self, devices, menu):
		super(Refresh_menu, self).__init__()
		self.quit = False
		self.hosts = []
		self.devices = devices
		self.menu = menu

	def update_menu(self):
		for i in self.menu.get_children():
			self.menu.remove(i)
			
		for host in self.hosts:
			menu_item = gtk.MenuItem(host)
			self.menu.append(menu_item)
			menu_item.show()
			
		control_menu_items(self.menu)
		
		hosts_notifier(self.hosts)
		return False

	def run(self):
		while not self.quit:
			self.refresh_hosts()
			gobject.idle_add(self.update_menu)
			time.sleep(5)
		 
			
	def refresh_hosts(self):
		self.hosts = []
		for device in self.devices:
			if not self.quit:
				self.hosts += get_hosts(device)
			
		return False

devices = get_interfaces()
menu = gtk.Menu()
control_menu_items(menu)

ind = appindicator.Indicator ("nadar",
						  "preferences-system-network",
						  appindicator.CATEGORY_APPLICATION_STATUS)
ind.set_status (appindicator.STATUS_ACTIVE)
ind.set_menu(menu)

pynotify.init("Nadar")

t = Refresh_menu(devices, menu)
t.start()
gtk.main()
os._exit(0)
