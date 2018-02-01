#!/usr/bin/python

import os.path, datetime, sys

import termcolor

datfile = "/opt/local/var/nagios/status.dat"

def main(infile):
  if os.path.exists(datfile) == False:
		print termcolor.colored("Nagios status file not found.  Check file path.", 'red', attrs=['bold'])
		return
	errfound = False
	while 1:
		line = infile.readline()
		if line == "":
			break
		if line[:4] == "host":
			x = host(infile)
			if(x):
				errfound = True
				print x
		if line[:7] == "service":
			x = service(infile)
			if(x):
				errfound = True
				print x
	return errfound

def info(infile):
	while 1:
		line = infile.readline()
		line = line.strip()
		if line == "}":
			break
		param = line.split("=")[0]
		if param == "created":
			t = long(line[8:])
			created = datetime.datetime.fromtimestamp(t)
	return created

def host(infile):
	while 1:
		host_name = ''
		current_state = '0'
		plugin_output = ''
		last_state_change = ''
		line = infile.readline()
		line = line.strip()
		if line == "}":
			break
		param = line.split("=")[0]
		if param == "host_name":
			host_name = line[10:]
		if param == "current_state":
			current_state = line[14:]
		if param == "plugin_output":
			plugin_output = line[14:]
		if param == "last_state_change":
			t = long(line[18:])
			last_state_change = datetime.datetime.fromtimestamp(t).strftime("%m/%d/%Y %I:%M %p")
	
	if current_state != "0":
		return '[%(date)s] [%(host)s] %(output)s' % dict(
			date	= termcolor.colored(last_state_change, 'yellow'),
			host	= host_name,
			output	= termcolor.colored('HOST DOWN: %s' % plugin_output, 'red'),
		)
	return None

def service(infile):
	current_state = '0'
	last_state_change = ''
	plugin_output = ''
	while 1:
		line = infile.readline()
		line = line.strip()
		if line == "}":
			break
		param = line.split("=")[0]
		if param == "host_name":
			host_name = line[10:]
		if param == "service_description":
			service_description = line[20:]
		if param == "current_state":
			current_state = line[14:]
		if param == "plugin_output":
			plugin_output = line[14:]
		if param == "last_state_change":
			t = long(line[18:])
			last_state_change = datetime.datetime.fromtimestamp(t).strftime("%m/%d/%Y %I:%M %p")
	
	if current_state != "0":
		return '[%(date)s] [%(host)s] %(output)s' % dict(
			date	= termcolor.colored(last_state_change, 'yellow'),
			host	= host_name,
			output	= termcolor.colored('%s: %s' % (service_description, plugin_output), 'red'),
		)
	return None

if(__name__ == '__main__'):
	infile = open(datfile, "r")
	if(main(infile)):
		sys.exit(1)
	else:
		print termcolor.colored('\n\nno nagios alerts at this time\n\n', 'green')
