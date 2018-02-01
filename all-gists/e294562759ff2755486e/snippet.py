# -*- coding: utf-8 -*-
import json
import urllib2
from M2Crypto import X509
from base64 import b64decode
from M2Crypto.Err import M2CryptoError

SNS_MESSAGE_TYPE_SUB_NOTIFICATION = "SubscriptionConfirmation"
SNS_MESSAGE_TYPE_NOTIFICATION = "Notification"
SNS_MESSAGE_TYPE_UNSUB_NOTIFICATION = "UnsubscribeConfirmation"

def canonical_message_builder(content, format):
    """ Builds the canonical message to be verified.

        Sorts the fields as a requirement from AWS

        Args:
            content (dict): Parsed body of the response
            format (list): List of the fields that need to go into the message
        Returns (str):
            canonical message
    """
    m = ""

    for field in sorted(format):
        try:
            m += field + "\n" + content[field] + "\n"
        except KeyError:
            # Build with what you have
            pass

    return str(m)


def verify_sns_notification(request):
    """ Takes a notification request from Amazon push service SNS and verifies the origin of the notification.

        Kudos to Artur Rodrigues for suggesting M2Crypto: http://goo.gl/KAgPPc

        Args:
            request (HTTPRequest): The request object that is passed to the view function
        Returns (bool):
            True if he message passes the verification, False otherwise
        Raises:
            ValueError: If the body of the response couldn't be parsed
            M2CryptoError: If an error raises during the verification process
            URLError: If the SigningCertURL couldn't be opened
    """
    cert = None
    pubkey = None
    canonical_message = None
    canonical_sub_unsub_format = ["Message", "MessageId", "SubscribeURL", "Timestamp", "Token", "TopicArn", "Type"]
    canonical_notification_format = ["Message", "MessageId", "Subject", "Timestamp", "TopicArn", "Type"]

    content = json.loads(request.body)
    decoded_signature = b64decode(content["Signature"])

    # Depending on the message type, canonical message format varies: http://goo.gl/oSrJl8
    if request.META.get("HTTP_X_AMZ_SNS_MESSAGE_TYPE", None) == SNS_MESSAGE_TYPE_SUB_NOTIFICATION or \
            request.META.get("HTTP_X_AMZ_SNS_MESSAGE_TYPE", None) == SNS_MESSAGE_TYPE_UNSUB_NOTIFICATION:

        canonical_message = canonical_message_builder(content, canonical_sub_unsub_format)

    elif request.META.get("HTTP_X_AMZ_SNS_MESSAGE_TYPE", None) == SNS_MESSAGE_TYPE_NOTIFICATION:

        canonical_message = canonical_message_builder(content, canonical_notification_format)

    else:
        raise ValueError("Message Type (%s) is not recognized" % request.META.get("HTTP_X_AMZ_SNS_MESSAGE_TYPE", None))

    # Load the certificate and extract the public key
    cert = X509.load_cert_string(str(urllib2.urlopen(content["SigningCertURL"]).read()))
    pubkey = cert.get_pubkey()
    pubkey.reset_context(md='sha1')
    pubkey.verify_init()

    # Feed the canonical message to sign it with the public key from the certificate
    pubkey.verify_update(canonical_message)

    # M2Crypto uses EVP_VerifyFinal() from openssl as the underlying verification function.
    # http://goo.gl/Bk2G36: "EVP_VerifyFinal() returns 1 for a correct signature, 0 for failure and -1 
    # if some other error occurred."
    verification_result = pubkey.verify_final(decoded_signature)

    if verification_result == 1:
        return True
    elif verification_result == 0:
        return False
    else:
        raise M2CryptoError("Some error occured while verifying the signature.")