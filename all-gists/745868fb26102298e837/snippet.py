import ssl
import sys
import optparse
import ConfigParser
import OpenSSL

def getCertificate(s):

        cert_pem = ssl.get_server_certificate((s, 443))
        cert_der = ssl.PEM_cert_to_DER_cert(cert_pem)
        x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert_pem)

        fingerprint = x509.digest('sha1')
        fingerprint = ':'.join(fingerprint[pos:pos+2] for pos in xrange(0,len(fingerprint),2))
        subject = x509.get_subject()

        print '%-25s %s' %('SHA1 Fingerprint:',fingerprint)
        print '%-25s %s' %('Serial Number:',x509.get_serial_number())
        print '%-25s %s' %('Common Name:',subject.CN)
        print '%-25s %s' %('Organization:',subject.O)
        print '%-25s %s' %('Issue Date:',x509.get_notBefore())
        print '%-25s %s' %('Expiration Date:', x509.get_notAfter())

        cert_out = open(s,'wb')
        cert_out.write(cert_pem)
        cert_out.close()


def readConfigs(args):
        usage = "Usage: python %prog [options] "
        parser = optparse.OptionParser(usage=usage)
        parser.add_option('--server', '-s', action='store', default=None, help='server to enumnerate')

        global options
        (options,server) = parser.parse_args(args)

def main(args):
        readConfigs(args)
        if options.server:
                getCertificate(options.server)

if __name__ == "__main__":
        args = sys.argv[1:]
        if args:
                main(args)
        else:
                print "See help (-h) for details"
                sys.exit(0)