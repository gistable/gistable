#!/usr/bin/python

import sys
import argparse, json, base64, struct
import urllib2
from datetime import datetime

LOGS = {
    'icarus': 'https://ct.googleapis.com/icarus',
    'pilot': 'https://ct.googleapis.com/pilot',
    'rocketeer': 'https://ct.googleapis.com/rocketeer',
    'skydiver': 'https://ct.googleapis.com/skydiver',

    'digicert1': 'https://ct1.digicert-ct.com/log',
    'digicert2': 'https://ct2.digicert-ct.com/log',

    'symantec': 'https://ct.ws.symantec.com',
    'vega': 'https://vega.ws.symantec.com',
    'sirius': 'https://sirius.ws.symantec.com',

    'venafi2': 'https://ctlog-gen2.api.venafi.com',

    'sabre': 'https://sabre.ct.comodo.com',
    'mammoth': 'https://mammoth.ct.comodo.com',

    'wosign': 'https://ctlog.wosign.com',
    'cnnic': 'https://ctserver.cnnic.cn',
    'startssl': 'https://ct.startssl.com',
    'gdca': 'https://ct.gdca.com.cn',
}

parser = argparse.ArgumentParser(description='Certificate Transparency submission client')
parser.add_argument('pem', type=argparse.FileType('r'), help='PEM files forming a certificate chain (with or without root)', nargs='+')
parser.add_argument('-o', dest='output', type=argparse.FileType('w'), help='output raw TLS extension data with all the SCTs (compatible with haproxy)')
parser.add_argument('-O', dest='output_dir', help='output individual SCTs to a directory (compatible with nginx-ct module)')

args = parser.parse_args()

chain = []
for pem in args.pem:
    for line in pem.readlines():
        line = line.strip()
        if len(line) == 0:
            continue

        if line == '-----BEGIN CERTIFICATE-----':
            cert = []
            continue
        elif line == '-----END CERTIFICATE-----':
            b64 = ''.join(cert)
            chain.append(b64)
            continue
        else:
            cert.append(line)

jsonRequest = json.dumps({'chain': chain})

scts = []
for log in sorted(LOGS.iterkeys()):
    print("sending request to %s" % LOGS[log])

    request = urllib2.Request(url = LOGS[log] + '/ct/v1/add-chain', data=jsonRequest)
    request.add_header('Content-Type', 'application/json')
    try:
        response = urllib2.urlopen(request)
        jsonResponse = response.read()
    except urllib2.HTTPError as e:
        if e.code >= 400 and e.code < 500:
            print("  unable to submit certificate to log, HTTP error %d %s: %s" % (e.code, e.reason, e.read()))
        else:
            print("  unable to submit certificate to log, HTTP error %d %s" % (e.code, e.reason))
        continue
    except urllib2.URLError as e:
        print("  unable to submit certificate to log, error %s" % e.reason)
        continue

    sct = json.loads(jsonResponse)
    print("  version: %d" % sct['sct_version'])
    print("  log ID: %s" % sct['id'])
    print("  timestamp: %d (%s)" % (sct['timestamp'], datetime.fromtimestamp(sct['timestamp'] / 1000)))
    print("  extensions: %s" % sct['extensions'])
    print("  signature: %s" % sct['signature'])

    logId = base64.b64decode(sct['id'])
    timestamp = sct['timestamp']
    extensions = base64.b64decode(sct['extensions'])
    signature = base64.b64decode(sct['signature'])
    sct = struct.pack('> B 32s Q H '+str(len(extensions))+'s '+str(len(signature))+'s', 0, logId, timestamp, len(extensions), extensions, signature)
    scts.append((log, sct))

    print("  SCT (%d bytes): %s" % (len(sct), base64.b64encode(sct)))

if args.output:
    size = 0
    for log, sct in scts:
        size += 2 + len(sct)
    args.output.write(struct.pack('>H', size))
    for log, sct in scts:
        args.output.write(struct.pack('>H '+str(len(sct))+'s', len(sct), sct))
    args.output.close()

if args.output_dir:
    for log, sct in scts:
        with open(args.output_dir + '/' + log + '.sct', 'w') as f:
            f.write(sct)
