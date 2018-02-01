#!/usr/bin/env python
#
# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <dev@robertweidlich.de> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return.
# ----------------------------------------------------------------------------
#


import sys

if len(sys.argv) < 2:
    print "Usage: %s hostname1 [hostname2] [hostname3] ..." % sys.argv[0]
    print
    print "Preparation:"
    print " $ virtualenv venv"
    print " $ . venv/bin/activate"
    print " $ pip install pytz pyasn1 pyOpenSSL ndg-httpsclient"

import ssl
from datetime import datetime
import pytz
import OpenSSL
import socket


from ndg.httpsclient.subj_alt_name import SubjectAltName
from pyasn1.codec.der import decoder as der_decoder
import pyasn1

def get_subj_alt_name(peer_cert):
    '''
    Copied from ndg.httpsclient.ssl_peer_verification.ServerSSLCertVerification
    Extract subjectAltName DNS name settings from certificate extensions

    @param peer_cert: peer certificate in SSL connection.  subjectAltName
    settings if any will be extracted from this
    @type peer_cert: OpenSSL.crypto.X509
    '''
    # Search through extensions
    dns_name = []
    general_names = SubjectAltName()
    for i in range(peer_cert.get_extension_count()):
        ext = peer_cert.get_extension(i)
        ext_name = ext.get_short_name()
        if ext_name == "subjectAltName":
            # PyOpenSSL returns extension data in ASN.1 encoded form
            ext_dat = ext.get_data()
            decoded_dat = der_decoder.decode(ext_dat, asn1Spec=general_names)

            for name in decoded_dat:
                if isinstance(name, SubjectAltName):
                    for entry in range(len(name)):
                        component = name.getComponentByPosition(entry)
                        dns_name.append(str(component.getComponent()))
    return dns_name

color = {
False: "\033[31;1m",
True: "\033[32;1m",
'end': "\033[0m",
'error': "\033[33;1m",
}

for server in sys.argv[1:]:
    ctx = OpenSSL.SSL.Context(ssl.PROTOCOL_TLSv1)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    x509 = None
    try:
        s.connect((server, 443))
        cnx = OpenSSL.SSL.Connection(ctx, s)
        cnx.set_tlsext_host_name(server)
        cnx.set_connect_state()
        cnx.do_handshake()

        x509 = cnx.get_peer_certificate()
        s.close()
    except Exception as e:
        print "%30s: %s%s%s" % (server, color['error'], e, color['end'])
        continue

    issuer = x509.get_issuer()
    issuer_corp = x509.get_issuer().organizationName
    issuer_url = x509.get_issuer().organizationalUnitName
    issuer_x509 = x509.get_issuer().commonName

    server_name = x509.get_subject().commonName
    server_name_ok = server_name == server

    try:
        subjectAltNames = get_subj_alt_name(x509)
    except pyasn1.error.PyAsn1Error:
        subjectAltNames = []
    server_name_alt_ok = server in subjectAltNames
    if server_name_alt_ok:
        server_name_alt = server
    elif len(subjectAltNames) == 0:
        server_name_alt = None
    else:
        server_name_alt = subjectAltNames[0]

    if len(subjectAltNames) > 1:
        server_name_alt += " (+%i)" % (len(subjectAltNames) - 1)

    now = datetime.now(pytz.utc)
    begin = datetime.strptime(x509.get_notBefore(), "%Y%m%d%H%M%SZ").replace(tzinfo=pytz.UTC)
    begin_ok = begin < now
    end = datetime.strptime(x509.get_notAfter(), "%Y%m%d%H%M%SZ").replace(tzinfo=pytz.UTC)
    end_ok = end > now

    print "%30s: %s%30s%s (alt: %s%30s%s) begin=%s%s%s end=%s%s%s issuer=%s" % (server,
        color[server_name_ok], server_name, color['end'],
        color[server_name_alt_ok], server_name_alt, color['end'],
        color[begin_ok], begin.strftime("%d.%m.%Y"), color['end'],
        color[end_ok], end.strftime("%d.%m.%Y"), color['end'],
        issuer_corp)
