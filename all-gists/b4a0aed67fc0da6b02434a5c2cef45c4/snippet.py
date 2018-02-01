#!/usr/bin/env python
import argparse
import hashlib
import sys

from eventlet import GreenPile

from swift.common import storage_policy
from swift.common import utils
from swift.common.bufferedhttp import http_connect

RING_DIR = '/etc/swift'

parser = argparse.ArgumentParser()
parser.add_argument('-P', '--policy', help="the name of the policy")
parser.add_argument('-o', '--output', action="store_true",
                    help="write body to stdout")
parser.add_argument('path', help="path to the object to get")


def get_policy(args):
    for policy in storage_policy.POLICIES:
        if not isinstance(policy, storage_policy.ECStoragePolicy):
            continue
        if not args.policy:
            break
        if policy.name == args.policy:
            break
    else:
        return 'ERROR: unable to find EC policy'
    policy.load_ring(RING_DIR)
    return policy


def _get_response(node, part, path, headers, policy):
    conn = http_connect(node['ip'], node['port'], node['device'],
                        part, 'GET', path, headers=headers)
    resp = conn.getresponse()
    data_len = int(resp.getheader('x-object-sysmeta-ec-content-length'))
    segment_size = int(resp.getheader('x-object-sysmeta-ec-segment-size'))
    # XXX: stinks to have to call this for every resp even though it's not
    # node specific
    fragment_size = policy.pyeclib_driver.get_segment_info(
        data_len, segment_size)['fragment_size']
    # TODO: something about resp.status
    resp.fragment_size = fragment_size
    return resp


def _get_one_fragment(resp, size):
    buff = ''
    remaining_bytes = size
    while remaining_bytes:
        chunk = resp.read(remaining_bytes)
        if not chunk:
            break
        remaining_bytes -= len(chunk)
        buff += chunk
    return buff


def main():
    args = parser.parse_args()
    policy = get_policy(args)
    try:
        account, container, obj = utils.split_path(
            args.path, minsegs=3, maxsegs=3, rest_with_last=True)
    except ValueError:
        return 'ERROR: invalid path %r' % args.path
    headers = {
        'X-Backend-Storage-Policy-Index': int(policy),
    }
    part, nodes = policy.object_ring.get_nodes(account, container, obj)

    pile = GreenPile(len(nodes))
    for node in nodes:
        pile.spawn(_get_response, node, part, args.path, headers, policy)

    responses = [resp for resp in pile]
    # TODO: if we don't have enough responses to rebuild bail

    h = hashlib.md5()
    while True:
        for resp in responses:
            pile.spawn(_get_one_fragment, resp, resp.fragment_size)
        fragment_payload = [fragment for fragment in pile if fragment]
        if not fragment_payload:
            break
        segment = policy.pyeclib_driver.decode(fragment_payload)
        h.update(segment)
        if args.output:
            sys.stdout.write(segment)
    sys.stderr.write('%s\n' % h.hexdigest())


if __name__ == "__main__":
    sys.exit(main())
