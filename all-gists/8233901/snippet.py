#!/usr/bin/env python
"""
Usage: check_ssl_certificate.py -H <host> -p <port> [-m <method>]
                      [-c <days>] [-w <days>]
  -h show the help
  -H <HOST>    host/ip to check
  -p <port>    port number
  -m <method>  (SSLv2|SSLv3|SSLv23|TLSv1) defaults to SSLv23
  -c <days>    day threshold for critical
  -w <days>    day threshold for warning
  -n name      Check CN value is valid
"""
# Courtesy of http://superuser.com/a/620192/259185

# On debian Based systems requires python-openssl

from __future__ import print_function

import getopt, sys
try:
  from OpenSSL import SSL
except:
  print('Failed to import OpenSSL. Please install pyOpenSSL')
  sys.exit(1)
import socket
import datetime


def print_usage():
    print(__doc__)


# FIXME rewrite with argparse
def get_options():
  "get options"

  options={
    'host':'',
    'port':'',
    'method':'SSLv23',
    'critical':5,
    'warning':15,
    'cn':'',
  }

  try:
    opts, args = getopt.getopt(sys.argv[1:], "hH:p:m:c:w:n:", ['help', "host", 'port', 'method'])
  except getopt.GetoptError as err:
    # print help information and exit:
    print(err) # will print something like "option -a not recognized"
    print_usage()
    sys.exit(2)
  for o, a in opts:
    if o in ("-h", "--help"):
      print_usage()
      sys.exit()
    elif o in ("-H", "--host"):
      options['host'] = a
      pass
    elif o in ("-p", "--port"):
      options['port'] = a
    elif o in ("-m", "--method"):
      options['method'] = a
    elif o == '-c':
      options['critical'] = int(a)
    elif o == '-w':
      options['warning'] = int(a)
    elif o == '-n':
      options['cn'] = a
    else:
      assert False, "unhandled option"

  if ('' == options['host'] or '' == options['port']):
    print_usage()
    sys.exit()

  if options['critical'] >= options['warning']:
    print("Critical must be smaller then warning")
    print_usage()
    sys.exit()

  return options


def main(options):
  ""
  # Initialize context
  if options['method']=='SSLv3':
    ctx = SSL.Context(SSL.SSLv3_METHOD)
  elif options['method']=='SSLv2':
    ctx = SSL.Context(SSL.SSLv2_METHOD)
  elif options['method']=='SSLv23':
    ctx = SSL.Context(SSL.SSLv23_METHOD)
  else:
    ctx = SSL.Context(SSL.TLSv1_METHOD)

  # Set up client
  sock = SSL.Connection(ctx, socket.socket(socket.AF_INET, socket.SOCK_STREAM))
  sock.connect((options['host'], int(options['port'])))
  # Send an EOF
  try:
    sock.send("\x04")
    sock.shutdown()
    peer_cert=sock.get_peer_certificate()
    sock.close()
  except SSL.Error as exc:
    print(exc)

  exit_status=0
  exit_message=[]

  cur_date = datetime.datetime.utcnow()
  cert_nbefore = datetime.datetime.strptime(peer_cert.get_notBefore(),'%Y%m%d%H%M%SZ')
  cert_nafter = datetime.datetime.strptime(peer_cert.get_notAfter(),'%Y%m%d%H%M%SZ')

  expire_days = int((cert_nafter - cur_date).days)

  if cert_nbefore > cur_date:
    if exit_status < 2: 
      exit_status = 2
    exit_message.append('C: cert is not valid')
  elif expire_days < 0:
    if exit_status < 2: 
      exit_status = 2
    exit_message.append('Expire critical (expired)')
  elif options['critical'] > expire_days:
    if exit_status < 2: 
      exit_status = 2
    exit_message.append('Expire critical')
  elif options['warning'] > expire_days:
    if exit_status < 1: 
      exit_status = 1
    exit_message.append('Expire warning')
  else:
    exit_message.append('Expire OK')

  exit_message.append('[{}d]'.format(expire_days))

  for part in peer_cert.get_subject().get_components():
    if part[0]=='CN':
      cert_cn=part[1]

  if options['cn'] != '' and options['cn'].lower() != cert_cn.lower():
    if exit_status < 2:
      exit_status = 2
    exit_message.append(' - CN mismatch')
  else:
    exit_message.append(' - CN OK')

  exit_message.append(' - cn:'+cert_cn)

  print(*exit_message)

  sys.exit(exit_status)

if __name__ == "__main__":
  main(get_options())
