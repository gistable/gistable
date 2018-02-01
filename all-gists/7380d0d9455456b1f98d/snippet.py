# Author: Cliff Lu <clifflu@gmail.com>
# License: Do whatever you want

import boto
import time
import json
from multiprocessing import Pool

def _harvest_region(region):
    """Build sub-map to that region. 

    Returns dict where keys are "%s%s" % (Architecture ["" for i386, "64" for i386-64], Virtualization ["pv", "hvm"])
    """
    ec2, images = region.connect(), {}
    
    def _latest(dictitem):
        """
        Expect dictitem as (key, set(...)), returns (key, maxval) while maxval is the latest ami in set(...)"""
        key, value = dictitem
        return key, max(value, key = lambda x: time.strptime(x.creationDate, "%Y-%m-%dT%H:%M:%S.%fZ"))

    for i in ec2.get_all_images(owners=['amazon'], filters={
        "name": "amzn-ami-*",
        "root-device-type": "ebs", 
    }): 
        if "amzn-ami-minimal" in i.name:
            continue

        images.setdefault("%s%s" % (
            "pv" if i.virtualization_type == 'paravirtual' else "hvm", # Virtualization
            "" if i.architecture == 'i386' else "64" # Architecture
        ), set()).add(i)

    return {arch: image.id for arch, image in map(_latest, images.items())}

def ami_tofu():
    """Scan latest AWS Linux AMI in all regions
    """
    regions = boto.connect_ec2().get_all_regions()
    p = Pool(len(regions))
    return dict(zip([r.name for r in regions], p.map(_harvest_region, regions)))

if __name__ == '__main__':
    print(json.dumps(ami_tofu(), indent=4))