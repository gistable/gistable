"""
Tools for creating a CA cert and signed server certs.
Divined from http://svn.osafoundation.org/m2crypto/trunk/tests/test_x509.py

The mk_temporary_xxx calls return a NamedTemporaryFile with certs.

Usage ;

   # Create a temporary CA cert and it's private key
   cacert, cakey = mk_temporary_cacert()
   # Create a temporary server cert+key, signed by the CA
   server_cert = mk_temporary_cert(cacert.name, cakey.name, '*.server.co.uk')

"""

from tempfile import NamedTemporaryFile as namedtmp
import time
from M2Crypto import X509, EVP, RSA, ASN1


__author__ = 'eskil@yelp.com'
__all__ = ['mk_temporary_cacert', 'mk_temporary_cert']


def mk_ca_issuer():
	"""
	Our default CA issuer name.
	"""
	issuer = X509.X509_Name()
	issuer.C = "US"
	issuer.CN = "ca_testing_server"
	issuer.ST = 'CA'
	issuer.L = 'San Francisco'
	issuer.O = 'ca_yelp'
	issuer.OU = 'ca_testing'
	return issuer


def mk_cert_valid(cert, days=365):
	"""
	Make a cert valid from now and til 'days' from now.
	Args:
	   cert -- cert to make valid
	   days -- number of days cert is valid for from now.
	"""
	t = long(time.time())
	now = ASN1.ASN1_UTCTIME()
	now.set_time(t)
	expire = ASN1.ASN1_UTCTIME()
	expire.set_time(t + days * 24 * 60 * 60)
	cert.set_not_before(now)
	cert.set_not_after(expire)


def mk_request(bits, cn='localhost'):
	"""
	Create a X509 request with the given number of bits in they key.
	Args:
	  bits -- number of RSA key bits
	  cn -- common name in the request
	Returns a X509 request and the private key (EVP)
	"""
	pk = EVP.PKey()
	x = X509.Request()
	rsa = RSA.gen_key(bits, 65537, lambda: None)
	pk.assign_rsa(rsa)
	x.set_pubkey(pk)
	name = x.get_subject()
	name.C = "US"
	name.CN = cn
	name.ST = 'CA'
	name.O = 'yelp'
	name.OU = 'testing'
	x.sign(pk,'sha1')
	return x, pk


def mk_cacert():
	"""
	Make a CA certificate.
	Returns the certificate, private key and public key.
	"""
	req, pk = mk_request(1024)
	pkey = req.get_pubkey()
	cert = X509.X509()
	cert.set_serial_number(1)
	cert.set_version(2)
	mk_cert_valid(cert)
	cert.set_issuer(mk_ca_issuer())
	cert.set_subject(cert.get_issuer())
	cert.set_pubkey(pkey)
	cert.add_ext(X509.new_extension('basicConstraints', 'CA:TRUE'))
	cert.add_ext(X509.new_extension('subjectKeyIdentifier', cert.get_fingerprint()))
	cert.sign(pk, 'sha1')
	return cert, pk, pkey


def mk_cert():
	"""
	Make a certificate.
	Returns a new cert.
	"""
	cert = X509.X509()
	cert.set_serial_number(2)
	cert.set_version(2)
	mk_cert_valid(cert)
	cert.add_ext(X509.new_extension('nsComment', 'SSL sever'))
	return cert


def mk_casigned_cert():
	"""
	Create a CA cert + server cert + server private key.
	"""
	# unused, left for history.
	cacert, pk1, _ = mk_cacert()
	cert_req, pk2 = mk_request(1024, cn='testing_server')
	cert = mk_cert(cacert)
	cert.set_subject(cert_req.get_subject())
	cert.set_pubkey(cert_req.get_pubkey())
	cert.sign(pk1, 'sha1')
	return cacert, cert, pk2


def mk_temporary_cacert():
	"""
	Create a temporary CA cert.
	Returns a tuple of NamedTemporaryFiles holding the CA cert and private key.
	"""
	cacert, pk1, pkey = mk_cacert()
	cacertf = namedtmp()
	cacertf.write(cacert.as_pem())
	cacertf.flush()

	pk1f = namedtmp()
	pk1f.write(pk1.as_pem(None))
	pk1f.flush()

	return cacertf, pk1f


def mk_temporary_cert(cacert_file, ca_key_file, cn):
	"""
	Create a temporary certificate signed by the given CA, and with the given common name.

	If cacert_file and ca_key_file is None, the certificate will be self-signed.

	Args:
	  cacert_file -- file containing the CA certificate
	  ca_key_file -- file containing the CA private key
	  cn -- desired common name
	Returns a namedtemporary file with the certificate and private key
	"""
	cert_req, pk2 = mk_request(1024, cn=cn)
	if cacert_file and ca_key_file:
		cacert = X509.load_cert(cacert_file)
		pk1 = EVP.load_key(ca_key_file)
	else:
		cacert = None
		pk1 = None

	cert = mk_cert()
	cert.set_subject(cert_req.get_subject())
	cert.set_pubkey(cert_req.get_pubkey())

	if cacert and pk1:
		cert.set_issuer(cacert.get_issuer())
		cert.sign(pk1, 'sha1')
	else:
		cert.set_issuer(cert.get_subject())
		cert.sign(pk2, 'sha1')

	certf = namedtmp()
	certf.write(cert.as_pem())
	certf.write(pk2.as_pem(None))
	certf.flush()

	return certf


if __name__ == '__main__':
	cacert, cert, pk = mk_casigned_cert()
	with open('cacert.crt', 'w') as f:
		f.write(cacert.as_pem())
	with open('cert.crt', 'w') as f:
		f.write(cert.as_pem())
		f.write(pk.as_pem(None))

	# Sanity checks...
	cac = X509.load_cert('cacert.crt')
	print cac.verify(), cac.check_ca()
	cc = X509.load_cert('cert.crt')
	print cc.verify(cac.get_pubkey())

# protips
# openssl verify -CAfile cacert.crt cacert.crt cert.crt
# openssl x509 -in cert.crt -noout -text
# openssl x509 -in cacert.crt -noout -text
