#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

A simple standalone script to test an Apple Push Notification setup.
Uses the feedback packets to provide the best information on how to fix things.

Steps to send a push notification:

* set up push certificates on your app on the developer portal and regenerate
  your provisioning profiles to make them push ready
* build your app with the new provisioning profile and enable push notifications
  in you app delegate
* run the app on your device and use NSLog to get its push token on
  the Xcode console
* select your push private key and certificate in Keychain and export them
  without a password as a p12 file
* run this command to convert your p12 file to a pem file:
  `$ openssl pkcs12 -nodes -in Push.p12 -out Push.pem` 
* run this command to make sure your certificates are valid:
  `$ openssl s_client -ssl3 -cert Push.pem -connect gateway.push.apple.com:2195`
  (use gateway.sandbox.push.apple.com if you have a dev push certificate)
  if they certificates are valid, the server should not hang up
* change the parameters at the end of the script and run it
* you should see the push notification come through or a helpful error message
* you may alter the JSON payload as you wish to test badges and meta data

"""

import socket
import ssl
import json
import binascii
import struct

def send_push(pem_file_path, token, message, production=True):
    """Send a push notification to the device."""

    # Prepare the binary payload
    token = token.strip().strip('<>').replace(' ','').replace('-', '')
    binary_token = binascii.unhexlify(token)
    payload = json.dumps({'aps': {'alert': message}})
    binary_payload = struct.pack(
        '!BiiH%dsH%ds' % (len(binary_token), len(payload)),
        1, 1337, 0,
        len(binary_token), binary_token, len(payload), payload
    )

    # Send the payload and wait 1 second for an error message
    print 'Connecting'
    apns_socket = ssl.wrap_socket(socket.socket(), certfile=pem_file_path, ssl_version=ssl.PROTOCOL_SSLv3)
    apns_socket.settimeout(1)
    apns_socket.connect((production and 'gateway.push.apple.com' or 'gateway.sandbox.push.apple.com', 2195))
    print 'Sending message "%s"' % message
    apns_socket.write(binary_payload)

    try:
        print 'Waiting for feedback'
        binary_response = apns_socket.recv(6)

        if len(binary_response) != 6:
            print 'The server hung up, please check your certificates and production mode setting'
        else:
            command, status, identifier = struct.unpack('!BBi', binary_response)

            if command != 8 or identifier != 1337:
                print 'Error receiving the feedback packet'
            else:
                status_messages = [
                    'Message successfully sent',
                    'Processing error',
                    'Missing device token',
                    'Missing topic',
                    'Missing payload',
                    'Invalid token size',
                    'Invalid topic size',
                    'Invalid payload size',
                    'Invalid topic size',
                    'Invalid token',
                ]

                if status >= 0 and status < len(status_messages):
                    print '%s (status %d)' % (status_messages[status], status)
                else:
                    print 'Unknown error (%d)' % status
    except ssl.SSLError, exc:
        if str(exc) == 'The read operation timed out':
            print 'Message succesfsfully send!'

    apns_socket.close()

if __name__ == '__main__':
    send_push(
        'Push.pem',
        'd274c466 16bb3ee5 07332af6 2f2b7474 b8c0e2ca 43fbe846 8287256b a71862db',
        u'Hello World!',
        production=True,
    )
