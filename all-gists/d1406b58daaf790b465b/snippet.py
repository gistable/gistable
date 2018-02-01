import sys, argparse, time, telnetlib
try:
	import socks
except ImportError:
	print("Proxy support is disabled.")
parser = argparse.ArgumentParser()
parser.add_argument("-e", "--email", help="The email to check")
parser.add_argument("-n", "--nameserver", help="The email server")
parser.add_argument("-p", "--nsport", help="The server port", type=int)
parser.add_argument("-t", "--timeout", help="The timeout in seconds", type=int)
parser.add_argument("-f", "--fake", help="The fake email address")
parser.add_argument("-E", "--extended", help="Use extended SMTP instead", action="store_true")
parser.add_argument("-P", "--proxy", help="The proxy location")
parser.add_argument("-o", "--port", help="The proxy port", type=int)
parser.add_argument("-T", "--type", help="The proxy type (HTTP, SOCKS4, SOCKS5")
args = parser.parse_args()
#Check if the user supplied an email.
if not args.email:
	print("You need to input an email.")
	sys.exit(1)
#Check if the user supplied an email server.
if not args.nameserver:	
	#Attempt to use a predefined email server
	print("Attempting to find the email server...")
	domain = args.email.split('@')[1]
	#This: https://github.com/mailcheck/mailcheck/wiki/List-of-Popular-Domains
	if (domain == "gmail.com" or domain == "googlemail.com"):
		args.nameserver = "gmail-smtp-in.l.google.com"
	elif (domain == "aol.com"):
		args.nameserver = "mailin-01.mx.aol.com"
	elif (domain == "att.net"):
		args.nameserver = "frf-mailrelay.att.net"
	elif (domain == "comcast.net"):
		args.nameserver = "mx1.comcast.net"
	elif (domain == "facebook.com"):
		args.nameserver = "msgin.vvv.facebook.com"
	elif (domain == "gmx.com" or domain == "mail.com"):
		args.nameserver = "mx00.gmx.net"
	elif (domain == "google.com"):
		args.nameserver = "aspmx.l.google.com"
	elif (domain == "hotmail.com" or domain == "hotmail.co.uk" or domain == "msn.com" or domain == "live.com"):
		args.nameserver = "mx1.hotmail.com"
	elif (domain == "mac.com" or domain == "me.com"):
		args.nameserver = "mx1.mail.icloud.com"
	elif (domain == "sbcglobal.net"):
		args.nameserver = "al-ip4-mx-vip1.prodigy.net"
	elif (domain == "verizon.net"):
		args.nameserver = "relay.verizon.net"
	elif (domain == "yahoo.com"):
		args.nameserver = "mta5.am0.yahoodns.net"
	elif (domain == "yahoo.co.uk"):
		args.nameserver = "mx-eu.mail.am0.yahoodns.net"
	else:
		print("You need to input an email server.")
		sys.exit(1)
	print("Email server set: " + args.nameserver)
#Check if the user supplied the email server port.
if not args.nsport:
	args.nsport = 25
#Check if the user supplied a timeout.
if not args.timeout:
	args.timeout = 3
#Check if the user supplied a fake email address.
if not args.fake:
	args.fake = "a@b.c"
#Get the domain from the email
domain = args.fake.split('@')[1]
#Check if the user supplied a proxy then wrap it
if args.proxy:
	#Check if the user supplied a proxy type
	if not args.type:
		args.type = "HTTP"
	if args.type == "HTTP":
		socks.setdefaultproxy(socks.PROXY_TYPE_HTTP, args.proxy, args.port)
	elif args.type == "SOCKS4":
		socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS4, args.proxy, args.port)
	elif args.type == "SOCKS5":
		socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, args.proxy, args.port)
	socks.wrapmodule(telnetlib)


telnet = telnetlib.Telnet(args.nameserver, args.nsport)
if args.extended:
	telnet.write("EHLO " + domain + "\r\n")
else:
	telnet.write("HELO " + domain + "\r\n")
telnet.write("MAIL FROM:<" + args.fake + ">\r\n")
telnet.write("RCPT TO:<" + args.email + ">\r\n")
telnet.write("QUIT\r\n")
time.sleep(args.timeout)
lines = telnet.read_all().split('\n')
accountExists = 0
for __ in lines:
	if (__.startswith("550")):
		accountExists = 0
		break
	elif (__.startswith("252")):
		accountExists = 2
		break
	elif (__.startswith("422") or __.startswith("431") or __.startswith("450")):
		accountExists = 3
		break
	else:
		accountExists = 1
if (accountExists == 3):
	print(args.email + " exists, but may not get your emails.")
elif (accountExists == 2):
	print(args.email + " may not exist.")
elif (accountExists):
	print(args.email + " exists!")
else:
	print(args.email + " doesn't exist!")
telnet.close()

