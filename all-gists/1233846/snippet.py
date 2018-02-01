#!/usr/bin/env python

# uses http://www.infrae.com/download/OAI/pyoai
from oaipmh.client import Client
from oaipmh.metadata import MetadataRegistry, oai_dc_reader

URL = 'http://researchcommons.waikato.ac.nz/dspace-oai/request'
registry = MetadataRegistry()
registry.registerReader('oai_dc', oai_dc_reader)
client = Client(URL, registry)


for record in client.listRecords(metadataPrefix='oai_dc'):
  print record[0].identifier()

