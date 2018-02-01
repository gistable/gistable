#!/usr/bin/env python

from boto.cloudsearch2.layer2 import Layer2

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--region', help='AWS region', required=True)
parser.add_argument('--domain', help='CloudSearch domain', required=True)
args = parser.parse_args()

conn_config = {
    'region': args.region,
    'debug': 0
}

conn = Layer2(**conn_config)
domain = conn.lookup(args.domain)
search = domain.get_search_service()
document_service = domain.get_document_service()

documents_present = True
while documents_present:
	all_docs = search.search(q="matchall", parser="structured", size=500)
	documents_present = len(all_docs) > 0
	for doc in all_docs:
		document_service.delete(doc['id'])
	document_service.commit()
