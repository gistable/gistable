import os
import socket
from OpenSSL import crypto, SSL

# OpenVPN is fairly simple since it works on OpenSSL. The OpenVPN server contains
# a root certificate authority that can sign sub-certificates. The certificates
# have very little or no information on who they belong to besides a filename
# and any required information. Everything else is omitted or blank.
# The client certificate and private key are inserted into the .ovpn file
# which contains some settins as well and the entire thing is then ready for
# the user.

# EasyRSA generates a standard unsigned certificate, certificate request, and private key.
# It then signs the certificate against the CA then dumps the certificate request in the trash.
# The now signed certificate and private key are returned.

# Create a new keypair of specified algorithm and number of bits.
def make_keypair(algorithm=crypto.TYPE_RSA, numbits=2048):
    pkey = crypto.PKey()
    pkey.generate_key(algorithm, numbits)
    return pkey

# Creates a certificate signing request (CSR) given the specified subject attributes.
def make_csr(pkey, CN, C=None, ST=None, L=None, O=None, OU=None, emailAddress=None, hashalgorithm='sha256WithRSAEncryption'):
    req = crypto.X509Req()
    req.get_subject()
    subj  = req.get_subject()

    if C:
        subj.C = C
    if ST:
        subj.ST = ST
    if L:
        subj.L = L
    if O:
        subj.O = O
    if OU:
        subj.OU = OU
    if CN:
        subj.CN = CN
    if emailAddress:
        subj.emailAddress = emailAddress

    req.set_pubkey(pkey)
    req.sign(pkey, hashalgorithm)
    return req

# Create a certificate authority (if we need one)
def create_ca(CN, C="", ST="", L="", O="", OU="", emailAddress="", hashalgorithm='sha256WithRSAEncryption'):
    cakey = make_keypair()
    careq = make_csr(cakey, cn=CN)
    cacert = crypto.X509()
    cacert.set_serial_number(0)
    cacert.gmtime_adj_notBefore(0)
    cacert.gmtime_adj_notAfter(60*60*24*365*10) # 10 yrs - hard to beat this kind of cert!
    cacert.set_issuer(careq.get_subject())
    cacert.set_subject(careq.get_subject())
    cacert.set_pubkey(careq.get_pubkey())
    cacert.set_version(2)

    # Set the extensions in two passes
    cacert.add_extensions([
        crypto.X509Extension('basicConstraints', True,'CA:TRUE'),
        crypto.X509Extension('subjectKeyIdentifier' , True , 'hash', subject=cacert)
    ])

    # ... now we can set the authority key since it depends on the subject key
    cacert.add_extensions([
        crypto.X509Extension('authorityKeyIdentifier' , False, 'issuer:always, keyid:always', issuer=cacert, subject=cacert)
    ])

    cacert.sign(cakey, hashalgorithm)
    return (cacert, cakey)

# Create a new subordinate cert.
def create_subordinate_certificate(csr, cakey, cacert, serial):
    cert = crypto.X509()
    cert.set_serial_number(serial)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(60*60*24*365*10) # 10 yrs - hard to beat this kind of cert!
    cert.set_issuer(cacert.get_subject())
    cert.set_subject(csr.get_subject())
    cert.set_pubkey(csr.get_pubkey())
    cert.set_version(2)

    extensions = []
    extensions.append(crypto.X509Extension('basicConstraints', False ,'CA:FALSE'))

    extensions.append(crypto.X509Extension('subjectKeyIdentifier' , False , 'hash', subject=cert))
    extensions.append(crypto.X509Extension('authorityKeyIdentifier' , False, 'keyid:always,issuer:always', subject=cacert, issuer=cacert))

    cert.add_extensions(extensions)
    cert.sign(cakey, 'sha256WithRSAEncryption')

    return cert

# Dumps content to a string
def dump_file_in_mem(material, format=crypto.FILETYPE_PEM):
    dump_func = None
    if isinstance(material, crypto.X509):
        dump_func = crypto.dump_certificate
    elif isinstance(material, crypto.PKey):
        dump_func = crypto.dump_privatekey
    elif isinstance(material, crypto.X509Req):
        dump_func = crypto.dump_certificate_request
    else:
        raise Exception("Don't know how to dump content type to file: %s (%r)" % (type(material), material))

    return dump_func(format, material)


# Loads the file into the appropriate openssl object type.
def load_from_file(materialfile, objtype, format=crypto.FILETYPE_PEM):
    if objtype is crypto.X509:
        load_func = crypto.load_certificate
    elif objtype is crypto.X509Req:
        load_func = crypto.load_certificate_request
    elif objtype is crypto.PKey:
        load_func = crypto.load_privatekey
    else:
        raise Exception("Unsupported material type: %s" % (objtype,))

    with open(materialfile, 'r') as fp:
        buf = fp.read()

    material = load_func(format, buf)
    return material

def retrieve_key_from_file(keyfile):
    return load_from_file(keyfile, crypto.PKey)

def retrieve_csr_from_file(csrfile):
    return load_from_file(csrfile, crypto.X509Req)

def retrieve_cert_from_file(certfile):
    return load_from_file(certfile, crypto.X509)


def make_new_ovpn_file(ca_cert, ca_key, clientname, serial, commonoptspath, filepath):

    # Read our common options file first
    f = open(commonoptspath, 'r')
    common = f.read()
    f.close()

    cacert = retrieve_cert_from_file(ca_cert)
    cakey  = retrieve_key_from_file(ca_key)

    # Generate a new private key pair for a new certificate.
    key = make_keypair()
    # Generate a certificate request
    csr = make_csr(key, clientname)
    # Sign the certificate with the new csr
    crt = create_subordinate_certificate(csr, cakey, cacert, serial)

    # Now we have a successfully signed certificate. We must now
    # create a .ovpn file and then dump it somewhere.
    clientkey  = dump_file_in_mem(key)
    clientcert = dump_file_in_mem(crt)
    cacertdump = dump_file_in_mem(cacert)
    ovpn = "%s<ca>\n%s</ca>\n<cert>\n%s</cert>\n<key>\n%s</key>\n" % (common, cacertdump, clientcert, clientkey)

    # Write our file.
    f = open(filepath, 'w')
    f.write(ovpn)
    f.close()


if __name__ == "__main__":
    make_new_ovpn_file("ca.crt", "ca.key", "justasictest", 0x0C, "common.txt", "justastictest.ovpn")
    print("Done")