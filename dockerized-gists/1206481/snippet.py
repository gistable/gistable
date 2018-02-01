import base64
import hmac
import hashlib
import urllib
import urllib2
import time
from datetime import datetime, tzinfo
from xml.dom import minidom


def upcase_compare(left, right):
    left = left.upper()
    right = right.upper()
    if(left < right):
        return -1
    elif(left > right):
        return 1
    return 0


class AmazonSignatureUtil:
    """
    This class performs the seemingly simple task of verifying a signature
    passed to the return url or IPN url from an Amazon Simple Payments button.
    It calls VerifySignature from the FPS (Flexible Payments Service) API.

    You will need:
    An AWS account access key and secret.

    Usage:
    sig_util = AmazonSignatureUtil('YOUR_ACCESS_KEY','YOUR_SECRET_KEY')
    sig_util.verify('http://example.com/success', {'params':'here'})
    """
    fps_sandbox_endpoint = 'https://fps.sandbox.amazonaws.com/'
    fps_prod_endpoint = 'https://fps.amazonaws.com/'
    aws_access_key = ''
    aws_secret_access_key = ''
    use_sandbox = True

    def __init__(self, access_key, secret_key, use_sandbox=True):
        self.aws_access_key = access_key
        self.aws_secret_access_key = secret_key
        self.use_sandbox = bool(use_sandbox)

    def verify(self, url_endpoint, params):
        """
        Performs an API request to VerifySignature passing along the
        parameters received from an Amazon Payment button.

        url_endpoint is the full return url you provided when you made your
        button. E.g. http://example.com/success

        params is a dict containing all the parameters that were passed back
        to your application, including the signature you wish to verify.
        """
        params = urllib.urlencode(params)

        values = {
            'Action': 'VerifySignature',
            'UrlEndPoint': url_endpoint,
            'HttpParameters': params,
            'AWSAccessKeyId': self.aws_access_key,
            'SignatureVersion': 2,
            'SignatureMethod': 'HmacSHA256',
            'Timestamp': time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            'Version': '2008-09-17',
        }

        data = self.get_signed_query(values)

        if self.use_sandbox == True:
            req = urllib2.Request(self.fps_sandbox_endpoint + '?%s' % data)
        else:
            req = urllib2.Request(self.fps_prod_endpoint + '?%s' % data)

        try:
            response = urllib2.urlopen(req)
            result = minidom.parseString(response.read())

            # parse response
            verify_sig_response = result.getElementsByTagName('VerifySignatureResponse')[0]
            verify_sig_result = verify_sig_response.getElementsByTagName('VerifySignatureResult')[0]
            verify_status = verify_sig_result.getElementsByTagName('VerificationStatus')[0]

            if 'Success' == verify_status.childNodes[0].data:
                return True
            else:
                return False

        except urllib2.HTTPError:
            # error response, no signature match
            return False

    def sign_string(self, string):
        """
        Strings going to and from the Amazon FPS service must be cryptographically
        signed to validate the identity of the caller.

        Sign the given string with the aws_secret_access_key using the SHA1 algorithm,
        Base64 encode the result and strip whitespace.

        NOTE: this was borrowed from the FyPS class
        """
        sig = base64.encodestring(hmac.new(self.aws_secret_access_key,
                                           string, hashlib.sha256)
                                           .digest()).strip()
        return(sig)

    def get_signed_query(self, parameters, signature_name='Signature'):
        """
        Returns a signed query string ready for use against the FPS REST
        interface. Encodes the given parameters and adds a signature
        parameter.

        NOTE: this was borrowed from the FyPS class
        """
        keys = parameters.keys()
        keys.sort(upcase_compare)
        message = ''
        for k in keys:
            message += "%s%s" % (k, parameters[k])
        sig = self.sign_string(message)

        parameters[signature_name] = sig
        return urllib.urlencode(parameters)
