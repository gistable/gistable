#!/usr/bin/python
import os, sys, getopt, socket
from pwd import getpwnam

def main():
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hd:u:t:s:", ["help", "domain="])
	except getopt.GetoptError, err:
		print str(err)
		usage()
		sys.exit(2)

	if len(opts) < 1:
		usage()
		sys.exit(2)

	for o, a in opts:
		if o in ("-h", "--help"):
			usage()
			sys.exit()
		if o in ("-d", "--domain"):
			domain = a


	directory = os.getcwd()
	vhost_template = open('/Users/paramah/internals/configuration/skel/vhost.conf').read()
	hosts_file = open('/etc/hosts').read();

	vhost = vhost_template.replace('@@dir@@', directory).replace('@@domain@@', domain)
	open('/Users/paramah/internals/configuration/sites/%s' % domain, 'w').write(vhost)

	hstring = "127.0.0.1 \t %s \n#@host@" % domain
	fhosts = hosts_file.replace('#@host@', hstring)
	open('/etc/hosts', 'w').write(fhosts)
	os.system('sudo nginx -s reload')

def usage():
  print 'usage: [-d domain.com]'

if __name__=="__main__":
	main()