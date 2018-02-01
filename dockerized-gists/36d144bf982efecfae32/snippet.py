#!/usr/bin/env python

import elasticsearch
import elasticsearch.helpers

esSrc = elasticsearch.Elasticsearch([{"host": "localhost", "port": 9200}])
esTar = elasticsearch.Elasticsearch([{"host": "localhost", "port": 9200}])
esTar.indices.delete(index="index_tar", ignore=[400, 404])
elasticsearch.helpers.reindex(client=esSrc, source_index="index_src", target_index="index_tar", target_client=esTar)
