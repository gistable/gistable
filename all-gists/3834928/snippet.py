# -*- mode: python; -*-
# Copyright 2009 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# To launch the app via the dev_appserver locally, run (from the google3 dir):
#
#   TARGET_PATH=dotorg/gongo/appengine_cap2kml
#   blaze build ${TARGET_PATH}:local
#   dev_appserver.py blaze-bin/$TARGET_PATH/bundle-local
#
# where the dev_appserver.py is from the Prometheus SDK or also available as
# /home/build/static/projects/apphosting/devtools/dev_appserver.py.
#
# To deploy the app, run (from the google3 dir):
#
#   PATH=dotorg/gongo/appengine-cap2kml
#   blaze build $PATH:prod
#   appcfg.py update blaze-bin/$PATH/prod
#
# BUILD techniques inspired by
# http://wiki.corp.google.com/Main/GnExplorerPrometheus

app = [FilesetEntry(files=glob(['*.py', '*.yaml']))]
templates = [FilesetEntry(files=glob(['*.html', '*.xml']))]
stylesheets = [FilesetEntry(srcdir='stylesheets', excludes=['.*~'],
                            destdir='stylesheets')]
testdata = [FilesetEntry(srcdir='testdata', excludes=['.*~'],
                         destdir='testdata')]
pyfo = [FilesetEntry(srcdir='//third_party/py/pyfo:BUILD',
                     files=['__init__.py'], destdir='pyfo')]
ui = [FilesetEntry(srcdir='ui', destdir='ui')]

# CAP library dynamically choses an XML parser.  In a google3 build, it would
# use cElementTree, but for AppEngine, this won't work because it relies on C
# code.  Since AppEngine has Python 2.5, it will use xml.etree.ElementTree
# instead, making this library "pure Python".
cap = [FilesetEntry(srcdir='//third_party/py/cap:BUILD',
                    excludes=['BUILD', 'LICENSE', 'setup.py'],
                    destdir='cap')]

iso8601 = [FilesetEntry(srcdir='//third_party/py/iso8601',
                        files=['__init__.py'],
                        destdir='iso8601')]

common_entries = (
    ui + app + templates + stylesheets + testdata + pyfo + cap + iso8601)

# We have separate "prod" and "local" targets in case we want to deploy
# differently when we push the live (prod) app.
prod_entries = common_entries
local_entries = common_entries

Fileset(name='prod', entries=common_entries, out='bundle-prod')
Fileset(name='local', entries=common_entries, out='bundle-local')

py_library(name = 'appengine_test_util',
           srcs = ['appengine_test_util.py'],
           deps = ['//apphosting/api:apiproxy_stub_map_py',
                   '//testing/pybase',
                   ],
           testonly = 1)

py_library(name = 'cap_crawl',
           srcs = ['cap_crawl.py'],
           deps = ['//apphosting/api:urlfetch_py',
                   '//apphosting/api/taskqueue:taskqueue_py',
                   '//apphosting/ext/db',
                   '//apphosting/ext/webapp',
                   '//apphosting/runtime:python_apiproxy_errors',
                   '//pyglib',
                   '//third_party/py/cap',
                   ':cap_fake',
                   ':cap_index_parse',
                   ':cap_parse_db',
                   ':cap_parse_mem',
                   ':cap_schema',
                   ':db_util',
                   ':webapp_util',
                   ':xml_util',
                   ],
           data = ['crawl.html',
                   'invalid_nudge.html',
                   ])

py_test(name = 'cap_crawl_integration_test',
        srcs = ['cap_crawl_integration_test.py'],
        deps = [':cap_crawl',
                ':cap_schema',
                ':db_test_util',
                ':fake_clock',
                ':taskqueue_test_util',
                ':web_query',
                '//pyglib',
                '//testing/pybase',
                '//third_party/py/mox',
                '//third_party/py/pytz',
                ],
        data = ['queue.yaml'],
        size = 'small')

py_test(name = 'cap_crawl_test',
        srcs = ['cap_crawl_test.py'],
        deps = [':cap_crawl',
                ':cap_index_parse',
                ':cap_parse_mem',
                ':cap_schema',
                ':cap_test_util',
                ':db_test_util',
                ':fake_clock',
                ':mox_util',
                ':taskqueue_test_util',
                '//apphosting/ext/db',
                '//apphosting/ext/webapp',
                '//apphosting/runtime:python_apiproxy_errors',
                '//testing/pybase',
                '//third_party/py/mox',
                ],
        size = 'small')

py_library(name = 'cap_fake',
           srcs = ['cap_fake.py'],
           data = glob(['testdata/*.xml']))

py_library(name = 'cap_index_parse',
           srcs = ['cap_index_parse.py'],
           deps = [':xml_util',
                   '//apphosting/runtime:python_apiproxy_errors',
                   ])

py_library(name = 'cap_mirror',
           srcs = ['cap_mirror.py'],
           deps = ['//apphosting/api:urlfetch_py',
                   '//apphosting/ext/db',
                   '//apphosting/ext/webapp',
                   '//third_party/py/cap',
                   ':cap_fake',
                   ':cap_parse_db',
                   ':cap_parse_mem',
                   ':cap_schema',
                   ':db_util',
                   ':paged_query',
                   ':webapp_util',
                   ':xml_util',
                   ],
           data = ['caps.html',
                   'crawl_header.html',
                   'crawls.html',
                   'crawls_purged.html',
                   'feeds.html',
                   'invalid_crawl.html',
                   'purge_crawls.html',
                   'shards.html',
                   'unknown_feed_list.html',
                   ])

py_test(name = 'cap_mirror_test',
        srcs = ['cap_mirror_test.py'],
        deps = [':cap_mirror',
                ':cap_schema',
                ':cap_test_util',
                ':db_test_util',
                ':fake_clock',
                ':mox_util',
                ':users_test_util',
                '//apphosting/ext/db',
                '//apphosting/ext/webapp',
                '//apphosting/runtime:python_apiproxy_errors',
                '//testing/pybase',
                '//third_party/py/mox',
                ],
        size = 'small')

py_library(name = 'cap_parse_db',
           srcs = ['cap_parse_db.py'],
           deps = [':cap_schema',
                   ':caplib_adapter',
                   ':model_parser',
                   '//pyglib',
                   ])

py_test(name = 'cap_parse_db_test',
        srcs = ['cap_parse_db_test.py'],
        deps = [':cap_parse_db',
                ':db_test_util',
                ':model_parser',
                '//pyglib',
                '//testing/pybase',
                '//third_party/py/cap',
                '//third_party/py/iso8601',
                '//third_party/py/mox',
                ],
        size = 'small')

py_library(name = 'cap_parse_mem',
           srcs = ['cap_parse_mem.py'],
           deps = [':cap_schema_mem',
                   ':caplib_adapter',
                   ':xml_util',
                   '//apphosting/runtime:python_apiproxy_errors',
                   ])

py_test(name = 'cap_parse_mem_test',
        srcs = ['cap_parse_mem_test.py'],
        deps = [':cap_parse_mem',
                '//testing/pybase',
                '//third_party/py/cap',
                ],
        data = ['testdata/aquila_cap2.xml'],
        size = 'small')

py_library(name = 'cap_schema',
           srcs = ['cap_schema.py'],
           deps = ['//apphosting/ext/db',
                   ':db_util',
                   ':web_query',
                   ])

py_library(name = 'cap_schema_mem',
           srcs = ['cap_schema_mem.py'],
           deps = ['//third_party/py/cap',
                   ])

py_test(name = 'cap_schema_mem_test',
        srcs = ['cap_schema_mem_test.py'],
        deps = [':cap_schema_mem',
                ':web_query',
                '//testing/pybase',
                ],
        size = 'small')

py_library(name = 'cap_test_util',
           srcs = ['cap_test_util.py'],
           deps = [':cap_schema'],
           testonly = 1)

py_library(name = 'caplib_adapter',
           srcs = ['caplib_adapter.py'])

py_library(name = 'db_test_util',
           srcs = ['db_test_util.py'],
           deps = [':appengine_test_util',
                   '//apphosting/api:datastore_file_stub',
                   '//apphosting/ext/db',
                   '//testing/pybase',
                   ],
           testonly = 1)

py_library(name = 'db_util',
           srcs = ['db_util.py'],
           deps = ['//apphosting/ext/db',
                   ])

py_test(name = 'db_util_test',
        srcs = ['db_util_test.py'],
        deps = ['//pyglib',
                '//testing/pybase',
                ':db_util',
                ],
        size = 'small')

py_library(name = 'fake_clock',
           srcs = ['fake_clock.py'],
           testonly = 1)

py_library(name = 'paged_query',
           srcs = ['paged_query.py'],
           data = ['pager.html'])

py_library(name = 'model_parser',
           srcs = ['model_parser.py'],
           deps = ['//apphosting/runtime:python_apiproxy_errors',
                   '//pyglib'])

py_library(name = 'mox_util',
           srcs = ['mox_util.py'],
           deps = ['//third_party/py/mox'],
           testonly = 1)

py_library(name = 'taskqueue_test_util',
           srcs = ['taskqueue_test_util.py'],
           deps = [':appengine_test_util',
                   '//apphosting/api/taskqueue:taskqueue_stub',
                   ],
           testonly = 1)

py_library(name = 'users_test_util',
           srcs = ['users_test_util.py'],
           deps = [':appengine_test_util',
                   '//apphosting/api:user_service_stub',
                   ],
           testonly = 1)

py_library(name = 'web_query',
           srcs = ['web_query.py'],
           deps = ['//pyglib'])

py_library(name = 'webapp_util',
           srcs = ['webapp_util.py'],
           deps = ['//apphosting/api:users_py',
                   '//apphosting/ext/webapp'])

py_library(name = 'xml_util',
           srcs = ['xml_util.py'],
           deps = ['//apphosting/ext/db',
                   '//apphosting/runtime:python_apiproxy_errors',
                   '//third_party/py/iso8601',
                   ])

py_test(name = 'xml_util_test',
        srcs = ['xml_util_test.py'],
        deps = [':db_util',
                ':xml_util',
                '//pyglib',
                '//testing/pybase',
                '//third_party/py/cap',
                '//third_party/py/iso8601',
                '//third_party/py/mox',
                ],
        size = 'small')
