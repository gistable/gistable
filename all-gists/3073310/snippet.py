#! /usr/bin/python

"""
    This simple script makes it easy to create server certificates
    that are signed by your own Certificate Authority.
    
    Mostly, this script just automates the workflow explained
    in http://www.tc.umn.edu/~brams006/selfsign.html.
    
    Before using this script, you'll need to create a private
    key and certificate file using OpenSSL. Create the ca.key
    file with:
    
        openssl genrsa -des3 -out ca.key 4096
    
    Then, create the ca.cert file with:
    
        openssl req -new -x509 -days 3650 -key ca.key -out ca.cert
    
    Put those files in the same directory as this script. 
    
    Finally, edit the values in this script's OPENSSL_CONFIG_TEMPLATE
    variable to taste.
    
    Now you can run this script with a single argument that is the name of
    a domain that you'd like to create a certificate for, e.g.:
    
        gencert.py mydomain.org
    
    The output will tell you where your server's certificate and
    private key are. The certificate will be valid for mydomain.org
    and all its subdomains.
    
    If you have any questions about this script, feel free to
    tweet @toolness or email me at varmaa@toolness.com.
    
    - Atul Varma, 5 March 2014
"""

import os
import sys
import hashlib
import subprocess
import datetime

OPENSSL_CONFIG_TEMPLATE = """
prompt = no
distinguished_name = req_distinguished_name
req_extensions = v3_req

[ req_distinguished_name ]
C                      = US
ST                     = IL
L                      = Chicago
O                      = Toolness
OU                     = Experimental Software Authority
CN                     = %(domain)s
emailAddress           = varmaa@toolness.com

[ v3_req ]
# Extensions to add to a certificate request
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectAltName = @alt_names

[ alt_names ]
DNS.1 = %(domain)s
DNS.2 = *.%(domain)s
"""

MYDIR = os.path.abspath(os.path.dirname(__file__))
OPENSSL = '/usr/bin/openssl'
KEY_SIZE = 1024
DAYS = 3650
CA_CERT = 'ca.cert'
CA_KEY = 'ca.key'

# Extra X509 args. Consider using e.g. ('-passin', 'pass:blah') if your
# CA password is 'blah'. For more information, see:
#
# http://www.openssl.org/docs/apps/openssl.html#PASS_PHRASE_ARGUMENTS
X509_EXTRA_ARGS = ()

def openssl(*args):
    cmdline = [OPENSSL] + list(args)
    subprocess.check_call(cmdline)

def gencert(domain, rootdir=MYDIR, keysize=KEY_SIZE, days=DAYS,
            ca_cert=CA_CERT, ca_key=CA_KEY):
    def dfile(ext):
        return os.path.join('domains', '%s.%s' % (domain, ext))

    os.chdir(rootdir)

    if not os.path.exists('domains'):
        os.mkdir('domains')

    if not os.path.exists(dfile('key')):
        openssl('genrsa', '-out', dfile('key'), str(keysize))

    config = open(dfile('config'), 'w')
    config.write(OPENSSL_CONFIG_TEMPLATE % {'domain': domain})
    config.close()

    openssl('req', '-new', '-key', dfile('key'), '-out', dfile('request'),
            '-config', dfile('config'))

    openssl('x509', '-req', '-days', str(days), '-in', dfile('request'),
            '-CA', ca_cert, '-CAkey', ca_key,
            '-set_serial',
            '0x%s' % hashlib.md5(domain + 
                                 str(datetime.datetime.now())).hexdigest(),
            '-out', dfile('cert'),
            '-extensions', 'v3_req', '-extfile', dfile('config'),
            *X509_EXTRA_ARGS)

    print "Done. The private key is at %s, the cert is at %s, and the " \
          "CA cert is at %s." % (dfile('key'), dfile('cert'), ca_cert)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "usage: %s <domain-name>" % sys.argv[0]
        sys.exit(1)
    gencert(sys.argv[1])
