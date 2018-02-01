from M2Crypto import SSL
from M2Crypto.SSL.Checker import SSLVerificationError, NoCertificate, WrongCertificate, WrongHost
import socket, re
from datetime import datetime
import pytz

class ValidationResults:
    
    def __init__(self):
        self.connection_error = False
        self.no_certificate = False
        self.wrong_certificate = False
        self.wrong_host = False
        self.certificate_expired = False
        self.expiration_date = None
        self.unknown_error = False
        self.inner_exception = None
        
    def __str__(self):
        return """
Connection error:\t%s
No certificate:\t\t%s
Wrong certificate:\t%s
Wrong host:\t\t%s
Certificate expired:\t%s
Expiration date:\t%s
Unknown error:\t\t%s
Inner exception:\t%s

        """ % (self.connection_error,
        self.no_certificate,
        self.wrong_certificate,
        self.wrong_host,
        self.certificate_expired,
        self.expiration_date,
        self.unknown_error,
        self.inner_exception,)
    
class Validator:
    
    numericIpMatch = re.compile('^[0-9]+(\.[0-9]+)*$')
    valid_hostname = False
    
    def __init__(self):
        pass
        
    def __call__(self, hostname, get_cert_from, port):
        val_results = ValidationResults()
                
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        cxt = SSL.Context()
        cxt.set_verify(SSL.verify_none, depth=1)

        SSL.Connection.clientPostConnectionCheck = None # we'll verify things later manually!

        try:
            c = SSL.Connection(cxt, sock)
            c.connect((get_cert_from, port))
            cert = c.get_peer_cert()
        except Exception, e:
            # socket connection
            val_results.connection_error = True
            val_results.inner_exception = e
            return val_results
            
        # NoCertificate WrongCertificate WrongHost ValueError
        try:
            c = SSL.Checker.Checker(hostname)
            c(cert)
        except NoCertificate:
            val_results.no_certificate = True
        except WrongCertificate:
            val_results.wrong_certificate = True
        except WrongHost:
            val_results.wrong_host = True
        except Exception, e:
            val_results.unknown_error = True
            val_results.inner_exception = e
        
        if cert.get_not_after().get_datetime() <= datetime.now(tz=pytz.utc):
            val_results.certificate_expired = True
            
        val_results.expiration_date = cert.get_not_after().get_datetime()
        
        return val_results

if __name__ == '__main__':
    get_cert_from = 'imap.gmail.com'
    hostname = 'imap.gmail.com'
    port = 993
    v = Validator()
    print v(hostname, get_cert_from, port)
    exit