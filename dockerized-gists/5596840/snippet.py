#!/usr/bin/python
#
#Notice:Please close domain lookup on your router or switch.
 
__author__="ring0"
__date__ ="$2011-6-5 16:00:00$"
__version__ ="0.3"
 
import sys
try:
	import pexpect
except:
	print "You must install pexpect module"
TIMEOUT=1
HOSTNAME="Router"
 
def exit_to_config(instance):
	'''
	Return to config mode,from config sub mode such as config-if,or multi level sub mode such as config-keychain-key.
	'''
	global TIMEOUT
	global HOSTNAME
	r_max=5
	instance.sendline('exit')
	i=instance.expect([HOSTNAME+'\(config\)#',pexpect.EOF,pexpect.TIMEOUT],TIMEOUT)
	if i==0:
		return True,"Back to config mode success."
	elif r_max<0:
		return False,"Exceed the maximum number of recursice."
	else:
		r_max=r_max-1
		exit_to_config(instance)
 
def login(hostip,password,hostname):
	'''
	Create pexpect instance,and login to Cisco device.
	'''
	global TIMEOUT
	global HOSTNAME
	HOSTNAME=hostname
	try:
		t=pexpect.spawn('telnet %s' % hostip)
	except:
		return False,"Can't create pexpect.spawn instance when call telnet command."
	i=t.expect(['Password:',pexpect.EOF,pexpect.TIMEOUT],TIMEOUT)
	if i==0:
		t.sendline(password)
	else:
		return False,"Connect to host failed,Please Check Router or Switch IP."
	i=t.expect([HOSTNAME+'>',pexpect.EOF,pexpect.TIMEOUT],TIMEOUT)
	if i==0:
		return t,"Login success."
	else:
		return False,"Login failed,Please check your password or hostname."
 
def privilege(instance,passwd=''):
	'''
	Enter privilege mode
	'''
	global TIMEOUT
	global HOSTNAME
	if not isinstance(instance,pexpect.spawn):
		return False,"Paremeter is not instance of pexpect.spawn."
 
	instance.sendline('')
	i=instance.expect([HOSTNAME+'#',pexpect.EOF,pexpect.TIMEOUT],TIMEOUT)
	if i==0:
		return True,"Already in privilege mode."
	if instance.isalive:
		instance.sendline('')
		i=instance.expect([HOSTNAME+'>',pexpect.EOF,pexpect.TIMEOUT],TIMEOUT)
		if i==0:
			instance.sendline('enable')
			i=instance.expect(['Password:',pexpect.EOF,pexpect.TIMEOUT],TIMEOUT)
			if i==0:
				instance.sendline(passwd)
				i=instance.expect([HOSTNAME+'#',pexpect.EOF,pexpect.TIMEOUT],TIMEOUT)
				if i==0:
					return True,"Entered privilege mode success."
				else:
					return False,'Enable password wrong.'
			else:
				return False,'Enable command failed'
	instance.sendline('')
	i=instance.expect([HOSTNAME+'\((.*)\)#',pexpect.EOF,pexpect.TIMEOUT],TIMEOUT)
	if i==0:
		instance.sendline('end')
		i=instance.expect([HOSTNAME+'#',pexpect.EOF,pexpect.TIMEOUT],TIMEOUT)
		if i==0:
			return True,"Back to privilege mode success."
		else:
			return False,"Back to privilege mode failed."
	return False,"Enter privilege failed."
 
def config(instance):
	'''
	Enter configure mode
	'''
	global HOSTNAME
	if not isinstance(instance,pexpect.spawn):
		return False,"paremeter is not instance of pexpect.spawn."
 
	if instance.isalive:
		instance.sendline('')
		i=instance.expect([HOSTNAME+'#',pexpect.EOF,pexpect.TIMEOUT],TIMEOUT)
		if i==0:
			instance.sendline('conf t')
			i=instance.expect([HOSTNAME+'\(config\)#',pexpect.EOF,pexpect.TIMEOUT],TIMEOUT)
			if i==0:
				return True,"Enter config mode success."
			else:
				return False,"Enter Config Mode failed from privilege mode."
	else:
		return False,'Please login first.'
 
	instance.sendline('')
	i=instance.expect([HOSTNAME+'\(config\)#',pexpect.EOF,pexpect.TIMEOUT],TIMEOUT)
	if i==0:
		return True,"Already in config mode."
	instance.sendline('')
	i=instance.expect([HOSTNAME+'\((.*)\)#',pexpect.EOF,pexpect.TIMEOUT],TIMEOUT)
	if i==0:
		return exit_to_config(instance)
 
def add_gw(instance,gw):
	'''
	Add default gateway
	'''
	global TIMEOUT
	global HOSTNAME
	if not isinstance(instance,pexpect.spawn):
		return False,"paremeter is not instance of pexpect.spawn."
	if instance.isalive:
		instance.sendline('')
		i=instance.expect([HOSTNAME+'\(config\)#',pexpect.EOF,pexpect.TIMEOUT],1)
		if i==0:
			instance.sendline('ip route 0.0.0.0 0.0.0.0 '+gw)
			return True,"Add default route success."
		else:
			return False,"This function must execute in Config Mode."
	else:
		return False,"Please login first."
 
def chg_gw(instance,o_gw,n_gw):
	'''
	Change default gateway
	'''
	global TIMEOUT
	global HOSTNAME
	if not isinstance(instance,pexpect.spawn):
		return False,"paremeter is not instance of pexpect.spawn."
	if instance.isalive:
		instance.sendline('')
		i=instance.expect([HOSTNAME+'\(config\)#',pexpect.EOF,pexpect.TIMEOUT],TIMEOUT)
		if i==0:
			instance.sendline('no ip route 0.0.0.0 0.0.0.0 '+o_gw)
			i=instance.expect(['No matching route to delete',pexpect.EOF,pexpect.TIMEOUT],TIMEOUT)
			if i==0:
				return False,"The old default route dons't exist."
			else:
				instance.sendline('ip route 0.0.0.0 0.0.0.0 '+n_gw)
				i=instance.expect([HOSTNAME+'\(config\)#',pexpect.EOF,pexpect.TIMEOUT],TIMEOUT)
				if i==0:
					return True,"Change default route success."
				else:
					return False,"Add new default route failed."
		else:
			return False,"Please enter config mode first."
	else:
		return False,"Please login first."
 
if __name__ == "__main__":
 
	route='1.1.1.5'
	password='hxsd'
	hostname='Router'
	enable='abc'
 
	(ret,msg)=login(route,password,hostname)
 
	if ret==False:
		sys.exit(msg)
	print msg
	telnet=ret
	(ret,msg)=privilege(telnet,enable)
	print msg
	if ret:
		(ret,msg)=config(telnet)
		print msg
		if ret:
			telnet.sendline('interface f0/0')
			(ret,msg)=config(telnet)
			print msg
			if ret:
				(ret,msg)=privilege(telnet)
				if ret:
					print msg
			(ret,msg)=config(telnet)
			print msg
			if ret:
				print add_gw(telnet,'1.1.1.7')[1]
				print chg_gw(telnet,'1.1.1.7','1.1.1.8')[1]
			telnet.sendline('key chain abc ')
			telnet.sendline('key 1')
			(ret,msg)=config(telnet)
			print msg
			if ret:
				print privilege(telnet)[1]
