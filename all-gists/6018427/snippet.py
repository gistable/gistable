# -*- coding: utf-8 -*-

"""
################################################################################
Dump ElasticSearch index for inserting BULK
################################################################################

requires `rawes`.

for more details, run `-h` to show help message.

`es-dump-index.py`: The simple script to dump the data from ElasticSearch for inserting by bulk API.


Usage
################################################################################

Dump all indices ::

        $ python es-dump-index.py --all http://127.0.0.1:9200/

Dump index ::

        $ python es-dump-index.py http://127.0.0.1:9200/index0

Dump index type ::

        $ python es-dump-index.py http://127.0.0.1:9200/index0/type0

To insert the dumped data, there are insert script in the dumped directory ::

        $ cd es_dump/<index>/<type>
        $ bash xxx.bulk.sh http://<elasticsearch server>/<new index>/<new type>

"""

import sys
import string
import os
import datetime
import time
import logging
import json
import argparse
import urlparse


try :
    import rawes
except ImportError :
    print '[error] %s requires `rawes`, install `$ pip install rawes`' % sys.argv[0]
    sys.exit(1)


FILENAME_INDEX_TYPE = '%(index)s.%(type)s-%%0%(n)dd.json'
FILENAME_INDEX_TYPE_WILDCARD = '%(index)s.%(type)s-*.json'
FILENAME_INDEX_TYPE_MAPPING = '%(index)s.%(type)s.mapping.json'
FILE_INDEX_TYPE_MAPPING = """{"__TYPE__": %s}"""
FILENAME_BULK_SCRIPT = '%(index)s.%(type)s.bulk.sh'
FILE_BULK_SCRIPT = """#!/bin/sh

# create from %(prog)s at %(created)s.

esserver=$1

if [ -z "$esserver" ];then
    echo "Usage: $0 http://<elastic server host and port>/<new index name>/<new type>"
    echo "	 Example) $0 http://localhost:9201/new-index/new-type"
    exit 1
fi

path=$(cd $(dirname ${BASH_SOURCE}); pwd)

# create index
curl -s -XPUT $(dirname $esserver) ; echo ''


# apply mapping
type=$(basename $esserver)
mapping=$(cat ${path}/%(filename_mapping)s | sed -e "s/__TYPE__/$type/g")
curl -s -XPUT $1/_mapping -d "$mapping"; echo ''
curl -s -XGET $1/_mapping?pretty=1; echo ''

# insert data
for i in ${path}/%(filename_index_type_wildcard)s
do
    curl -s -XPOST "$1/_bulk" --data-binary @${i}; echo ''
done

# end
"""

################################################################################
# option
parser = argparse.ArgumentParser(
        description='Dump elasticsearch index to json-like data for bulk insert.'
    )
parser.add_argument(
        'server',
        help='elasticsearch url',
    )

parser.add_argument(
        '--all',
        dest='all',
        action='store_true',
        default=False,
        help='dump all indices',
    )

parser.add_argument(
        '--ignore-id',
        dest='ignore_id',
        action='store_true',
        default=False,
        help='ignore the document id',
    )

parser.add_argument(
        '-d',
        dest='debug',
        action='store_true',
        default=False,
        help='debug',
    )

parser.add_argument(
        '--dump',
        default='es_dump',
        help='dump directory',
    )

parser.add_argument(
        '--logfile',
        help='log file',
    )

parser.add_argument(
        '--split',
        default=30000,
        help='split index dump.',
    )

################################################################################


def _get_file_index_type (filename, n, ) :
    return file(filename % n, 'wb', )


def _get_mapping (conn, index, _type=None, ) :
    _index_prefix = index
    if _type :
        _index_prefix += '/' + _type

    return conn.get('%s/_mapping' % (_index_prefix, ), )


def _dump_index_type (conn, dump, index, _type, ) :
    _it = '%s/%s' % (index, _type, )

    logging.debug('[%s] dump directory, "%s" created' % (_it, _dump, ), )
    logging.debug('[%s] trying to dump' % _it, )

    # get data using `_search/scroll`
    logging.debug('[%s] /%s/_search' % (_it, _it, ), )
    _o = conn.get(
            '%s/_search' % _it,
            data={"query": {"match_all": {}}},
            params=dict(
                    search_type='scan',
                    scroll='10m',
                    size=int(LIMIT / 4) if LIMIT > 10000 else LIMIT,
                    pretty=1,
                ),
        )

    _total = _o.get('hits').get('total')
    yield _total

    logging.debug('[%s] total: %d' % (_it, _total, ), )
    if _total < 1 :
        logging.debug('nothing happened, total: %d' % _total, )
        sys.exit(1)


    _scroll_id = _o.get('_scroll_id')
    logging.debug('[%s] scroll id: %s' % (_it, _scroll_id, ), )

    # create mapping data

    # create dump data
    logging.debug('[%s] trying to _search/scroll' % (_it, ), )
    _left = _total
    while True :
        if _left < 1 :
            break
    
        _o = conn.get(
                '_search/scroll',
                data=_scroll_id,
                params=dict(
                        scroll='10m',
                        pretty=1,
                    ),
            )
        _total = _o.get('hits').get('total')
        _left -= len(_o.get('hits').get('hits'))
    
        logging.debug('[%s] scroll: %d, left: %d' % (_it, _left, len(_o.get('hits').get('hits'))), )
    
        for i in _o.get('hits').get('hits') :
            _i = i.copy()
            _source = _i.get('_source')
            del _i['_score']
            del _i['_source']
            del _i['_index']
            del _i['_type']
            if CONFIG.ignore_id :
                del _i['_id']
    
            yield dict(create=_i, ), _source
    
        time.sleep(0.01, )

    logging.debug('[%s] dumped' % (_it, ), )

    # return


CONFIG = parser.parse_args()

################################################################################
# check argument
if CONFIG.debug :
    _logfile = CONFIG.logfile if CONFIG.logfile else None

    logging.basicConfig(filename=_logfile, level=logging.DEBUG, )

try :
    LIMIT = int(CONFIG.split, )
except (TypeError, ValueError, ) :
    parser.error('--split value must be int.', )


_u = urlparse.urlparse(CONFIG.server, )
INDEX, TYPE = (filter(
        string.strip, map(lambda x : x.replace('/', '', ), _u.path.rsplit('/', 1, ), ),
    ) + [None, None, ])[:2]

_server = urlparse.urlunparse(list(_u)[:2] + ['', '', '', '', ])

logging.debug('> trying to dump data from "%s", index: "%s", type: "%s".' % (
        _server,
        INDEX if INDEX else '',
        TYPE if TYPE else '',
    ), )

# dump directory
if not os.path.exists(CONFIG.dump, ) :
    os.makedirs(CONFIG.dump, )
    #parser.error('dump directory, "%s" already exists' % CONFIG.dump, )

################################################################################

conn = rawes.Elastic(_server, timeout=200, )

_indices_and_types = dict()
_all_indices = conn.get('_aliases', ).keys()

if INDEX :
    # index and types
    if INDEX not in _all_indices :
        parser.error('the index, "%s" does not exist.' % INDEX, )
    
    _mappings = _get_mapping(conn, INDEX, ).get(INDEX, )
    if TYPE : # get all type
        if TYPE not in _mappings.keys() :
            parser.error('the type, "%s" does not exist in this index, "%s".' % (TYPE, INDEX, ), )
    
        _indices_and_types[INDEX] = {TYPE: _mappings.get(TYPE, ), }
    else :
        _indices_and_types[INDEX] = _mappings
elif CONFIG.all :
    _indices_and_types = dict(map(lambda x : (x, _get_mapping(conn, x, ).get(x, ), ), _all_indices, ), )
else :
    parser.error('index name must be given or to dump all indices, use `--all` option', )


for _index, _mappings in _indices_and_types.items() :
    # create directory
    _dump = os.path.join(CONFIG.dump, _index, )
    if not os.path.exists(_dump, ) :
        os.makedirs(_dump, )

    for _type, _mapping in _mappings.items() :

        _first = True
        _n = 0
        for i in _dump_index_type(conn, CONFIG.dump, _index, _type, ) :
            if _first :
                _filename_index_type = FILENAME_INDEX_TYPE % dict(
                        index=_index,
                        type=_type,
                        n=len(str(i / LIMIT)),
                    )

                _target = _get_file_index_type(os.path.join(_dump, _filename_index_type, ), 0, )
                _first = False
                continue

            _target.write(json.dumps(i[0], ) + '\n', )
            _target.write(json.dumps(i[1], ) + '\n', )
            _n += 1

            if _n % LIMIT == 0 :
                _target.write('\n', )
                _target.close()

                _target = _get_file_index_type(os.path.join(_dump, _filename_index_type, ), int(_n / LIMIT), )

        _target.write('\n', )
        _target.close()

        # store mapping data
        _filename_mapping = FILENAME_INDEX_TYPE_MAPPING % dict(index=_index, type=_type, )
        with file(os.path.join(_dump, _filename_mapping, ), 'wb', ) as _target :
            _target.write(FILE_INDEX_TYPE_MAPPING % json.dumps(_mapping, indent=4, ), )

        # create bulk insert script
        _filename_bulk_insert = FILENAME_BULK_SCRIPT % dict(index=_index, type=_type, )
        with file(os.path.join(_dump, _filename_bulk_insert, ), 'wb', ) as _target :
            _target.write(
                FILE_BULK_SCRIPT % dict(
                        prog=sys.argv[0],
                        created=datetime.datetime.now().isoformat(),
                        filename_index_type=_filename_index_type,
                        filename_mapping=_filename_mapping,
                        filename_index_type_wildcard = FILENAME_INDEX_TYPE_WILDCARD % dict(
                                index=_index,
                                type=_type,
                            ),
                    )
                )


logging.debug('< done', )

sys.exit(0)

