#!/usr/bin/env python
import sys
from argparse import ArgumentParser

from swift.common.direct_client import direct_get_suffix_hashes
from swift.common.storage_policy import POLICIES

parser = ArgumentParser()
parser.add_argument('--policy-index', default=0, help='policy index')
parser.add_argument('part', help='the part')
parser.add_argument('-s', '--suffix', nargs='*',
                    help='any suffixes to recalculate')
parser.add_argument('-d', '--device', help='limit command to single node')


def main():
    args = parser.parse_args()

    policy = POLICIES[args.policy_index]

    policy.load_ring('/etc/swift/')
    ring = policy.object_ring

    suffixes = args.suffix or []
    for node in ring.devs:
        if node is None:
            continue
        if args.device and node['device'] != args.device:
            continue
        data = direct_get_suffix_hashes(
            node, args.part, suffixes, headers={
                'x-backend-storage-policy-index': int(policy)})
        print node['ip'], node['port'], node['device']
        print data

if __name__ == "__main__":
    sys.exit(main())
