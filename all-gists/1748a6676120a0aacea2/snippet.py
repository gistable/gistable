#!/usr/bin/env python
#
# DNS Result Comparison Utility
# Author: https://twitter.com/chair6
#

import argparse
import dns.resolver
import dns.rdatatype
from collections import defaultdict
from hashlib import sha1

DEFAULT_RESOLVERS = ['8.8.8.8', '8.8.4.4']
DEFAULT_RECORD_TYPE = ['A', 'MX']

VERBOSE = False


def initialize():
    parser = argparse.ArgumentParser(
        description='DNS Result Comparison Utility'
    )
    parser.add_argument(
        '-t', '--types', dest='record_types', metavar='record_type',
        action='store', default=DEFAULT_RECORD_TYPE, type=str, nargs='*',
        help='Type of record to query (default: {0})'.format(
            ', '.join(DEFAULT_RECORD_TYPE)
        )
    )
    parser.add_argument(
        '-r', '--resolvers', dest='resolvers', metavar='resolver',
        action='store', default=DEFAULT_RESOLVERS, type=str, nargs='*',
        help='List of resolvers to query (default: {0})'.format(
            ' '.join(DEFAULT_RESOLVERS)
        )
    )
    parser.add_argument(
        '-v', '--verbose', dest='verbose',
        action='store_true', default=False,
        help='Include detailed results in output'
    )
    parser.add_argument(
        'names',  metavar='record', action='store', type=str, nargs='*',
        help='Name of the DNS record/s to query during testing'
    )
    args = parser.parse_args()

    for rt in args.record_types:
        try:
            dns.rdatatype.from_text(rt)
        except dns.rdatatype.UnknownRdatatype:
            args.record_types = [x for x in args.record_types if x != rt]
            print(
                '** Invalid record type specified ({0}), skipping.'
                .format(rt)
            )
    if len(args.resolvers) == 0:
        parser.error('No DNS resolvers specified to test against.')
    if len(args.record_types) == 0:
        parser.error('No valid record types identified.')
    if len(args.names) == 0:
        parser.error('No DNS record/s specified.')

    return (args.resolvers, args.names, args.record_types, args.verbose)


def diff(resolvers, names, record_types):
    results_by_resolver = defaultdict(defaultdict)
    results_signatures = defaultdict(defaultdict)
    resolver = dns.resolver.Resolver(configure=False)
    for r in resolvers:
        results_by_resolver[r] = defaultdict(defaultdict)
        results_signatures[r] = defaultdict(defaultdict)
        for rn in names:
            results_by_resolver[r][rn] = defaultdict(list)
            results_signatures[r][rn] = defaultdict(defaultdict)
            for rt in record_types:
                results_signatures[r][rn][rt] = set()
                resolver.nameservers = [r]
                result = None
                try:
                    answers = dns.resolver.query(rn, rt)
                except dns.resolver.NXDOMAIN:
                    result = 'NXDOMAIN'
                except dns.resolver.NoAnswer:
                    result = 'NO ANSWER'
                if result is not None:
                    results_by_resolver[r][rn][rt].append(result)
                else:
                    # save individual answers from query response
                    for rdata in answers:
                        results_by_resolver[r][rn][rt].append(rdata.to_text())
                    # build signature for this query response
                    result = '::'.join(
                        sorted([rdata.to_text() for rdata in answers])
                    )
                    results_signatures[r][rn][rt].add(sha1(result).hexdigest())
    return (results_by_resolver, results_signatures)


def report(results_by_resolver, results_signatures, counts):
    inconsistent = False
    for r in results_by_resolver:
        for rn in results_by_resolver[r]:
            for rt in results_by_resolver[r][rn]:
                if len(results_signatures[r][rn][rt]) > 1:
                    inconsistent = True

    print(
        "\nTesting completed against {0} resolvers, {1} names, and {2} types."
        .format(counts[0], counts[1], counts[2])
    )
    if inconsistent:
        print("** Inconsistent query answers detected.\n")
    else:
        print("Query answers consistent across all resolvers tested.\n")

    if VERBOSE:
        for r in results_by_resolver:
            print("Resolver : {0}".format(r))
            for rn in results_by_resolver[r]:
                print("\tTarget DNS name: {0}".format(rn))
                for rt in results_by_resolver[r][rn]:
                    print("\t\t{0} answers:\n\t\t\t{1}\n".format(
                        rt,
                        '\n\t\t\t'.join(results_by_resolver[r][rn][rt])
                    ))


if __name__ == '__main__':
    (resolvers, names, record_types, VERBOSE) = initialize()
    counts = (len(resolvers), len(names), len(record_types))
    (by_resolver, signatures) = diff(resolvers, names, record_types)
    report(by_resolver, signatures, counts)