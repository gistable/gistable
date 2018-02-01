#
# Comic Chat fixer MITM proxy: fixes Comic Chat to (sort of) work with modern
# IRC servers. Tested with Microsoft Chat 2.5 on Windows XP, 8 and 10
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#

import getopt, re, socket, sys, threading, time
try:
	import ssl
except ImportError:
	ssl = None

def thread_c2s(client, client_addr, password, host, port, use_ssl):
	f = client.makefile()
	
	queued_lines = []
	if password:
		client.sendall(':cchat.proxy 464 * :Password incorrect\r\n')
		while True:
			line = f.readline().rstrip('\r\n')
			if line[:12] == 'OPER (null) ':
				if password == line[12:]:
					print '[-] {0}:{1} authenticated successfully'.format(*client_addr)
					break
				else:
					print '[!] {0}:{1} failed to authenticate'.format(*client_addr)
					client.sendall(':cchat.proxy 464 * :Password incorrect\r\n')
			else:
				queued_lines.append(line)
	
	irc = socket.create_connection((host, port))
	if use_ssl:
		if not ssl: raise Exception('no ssl module')
		irc = ssl.wrap_socket(irc)
	
	for line in queued_lines:
		irc.sendall(line + '\r\n')
	
	t = threading.Thread(target=thread_s2c, args=(client, client_addr, irc))
	t.daemon = True
	t.start()
	
	try:
		while True:
			line = f.readline()
			irc.sendall(line)
			if len(line) == 0 or line[:5] == 'QUIT ': break
	except KeyboardInterrupt:
		sys.exit(1)
	except:
		pass
	
	try:
		irc.close()
	except:
		pass
	try:
		client.close()
	except:
		pass

def thread_s2c(client, client_addr, irc):
	f = irc.makefile()
	
	srv_prefix = '@+'
	
	try:
		while True:
			line = f.readline()
			
			split = line.split(' ')
			if len(split) > 2:
				if split[0] == 'ERROR':
					client.sendall(line)
					break
				elif split[1] == '005':
					# Get PREFIX= to fix ranks in the NAMES response
					match = re.search(''' PREFIX=\(([^\)]+)\)([^\s]+)''', line)
					if match:
						srv_prefix = match.group(2)
				elif split[1] == 'JOIN' and split[2][0] != ':':
					# Main purpose of the proxy. Fixes a crash bug with newer
					# ircds, which send JOIN confirmations like this:
					# 
					#   :nick!user@host JOIN #channel
					#
					# instead of this:
					#
					#   :nick!user@host JOIN :#channel
					# 
					# CChat expects the channel name to have a : before the
					# name. If it doesn't, it will crash, since it somehow
					# attempts a stricmp(0).
					split[2] = ':' + split[2]
				elif split[1] == '353':
					# Convert additional ranks to regular op
					for i in range(5, len(split)):
						rank = ''
						nick = ''
						for char in split[i]:
							if char == '+' and rank != '@':
								# voice
								rank = '+'
							elif char in srv_prefix:
								# everything unknown to CChat becomes op
								rank = '@'
							elif char != ':':
								# not a rank
								nick += char
						split[i] = (split[i][0] == ':' and ':' or '') + rank + nick
				line = ' '.join(split)
			
			# Comic Chat will stop receiving if it receives a line longer than
			# 512 bytes, including the trailing CRLF.
			client.sendall(line.rstrip('\r\n')[:510] + '\r\n')
	except KeyboardInterrupt:
		sys.exit(1)
	
	try:
		irc.close()
	except:
		pass
	try:
		client.close()
	except:
		pass

def main():
	bind_host = ''
	bind_port = 6461
	password = None
	
	options, remainder = getopt.getopt(sys.argv[1:], 'h:p:a:', ['bindhost=', 'bindport=', 'password='])
	for opt, arg in options:
		if opt in ('-h', '--bindhost'):
			bind_host = arg
		elif opt in ('-p', '--bindport'):
			bind_port = int(arg)
		elif opt in ('-a', '--password'):
			password = arg
	
	if bind_port < 0 or bind_port > 65535 or len(remainder) < 1:
		print 'Usage: proxy.py [-h bindhost] [-p bindport] [-a password] server [[+]port]'
		sys.exit(1)
	
	host = remainder[0]
	if len(remainder) > 1:
		if remainder[1][0] == '+':
			use_ssl = True
			port = int(remainder[1][1:])
		else:
			use_ssl = False
			port = int(remainder[1])
	else:
		use_ssl = False
		port = 6667
	
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server.bind((bind_host, bind_port))
	server.listen(5)
	
	print '[-] Waiting for connections'
	
	try:
		while True:
			client, client_addr = server.accept()
			print '[-] Connection from {0}:{1}'.format(*client_addr)
			t = threading.Thread(target=thread_c2s, args=(client, client_addr, password, host, port, use_ssl))
			t.daemon = True
			t.start()
	except KeyboardInterrupt:
		server.close()
		sys.exit(1)

if __name__ == '__main__':
	main()
