#!/usr/bin/env python

# Script to query Dell's API for the hardware's original config.
# Just drop your service tag as parameters for the script and go.

import sys
import requests

APIKEY = 'd676cf6e1e0ceb8fd14e8cb69acd812d'
URL = 'https://api.dell.com/support/v2/assetinfo/detail/tags.json?svctags={0}&apikey=' + APIKEY

def get_parts(svctag):
    res = requests.get(URL.format(svctag))

    if res.status_code != 200:
        sys.stderr.write('[%s] Caught %i as the response code.\n' % (svctag, res.status_code))
        sys.stderr.write('[%s] Unable to get details for given service tag.\n'
                % svctag)
        return False

    fault = res.json['GetAssetDetailResponse']['GetAssetDetailResult']['Faults']
    if fault is not None:
        sys.stderr.write("[%s] Failed to find details. Sure it's a valid TAG?\n" % svctag )
        return False

    asset = res.json['GetAssetDetailResponse']['GetAssetDetailResult']['Response']['DellAsset']
    model = asset['MachineDescription']
    parts = asset['AssetParts']['AssetPart']

    print 'Model:    ', model
    print '{0:<10} {1:<15} {2:>10}'.format(*('Quantity','PartNumber','Description'))
    for part in [(d['Quantity'],d['PartNumber'],d['PartDescription']) for d in parts]:
        print '{0:<10} {1:<15} {2:>10}'.format(*part)

if __name__ == '__main__':
    get_parts(sys.argv[1])
    sys.exit()
