'''
Convert information from a firefox sqlite db to json
document:
http://www.forensicswiki.org/wiki/Mozilla_Firefox_3_History_File_Format 
'''
import sqlite3 
import time
import datetime 
import os
import sys
import json 

def connect_db_and_fetchall(db, table):
    con = sqlite3.connect(db)
    c = con.cursor()
    c.execute('pragma table_info(%s)' % table)
    con.commit()
    columns = [x[1] for x in c.fetchall()] 
    c.execute('select * from %s' % table)
    con.commit() 
    result = []
    for row in c.fetchall(): 
        result.append(dict(zip(columns, row)))
    return result

def read_history(db): 
    '''eg:
     {u'fieldname': u'searchbar-history',
      u'firstUsed': 1398326735527000L,
      u'guid': u'xzxXhLVkQjKaXDd/',
      u'id': 6139,
      u'lastUsed': 1398326735527000L,
      u'timesUsed': 1,
      u'value': u'python sqlite'}]
    '''  
    return connect_db_and_fetchall(db, "moz_formhistory")

def read_cookies(db): 
    '''eg:
     {u'appId': 0,
      u'baseDomain': u'xxx.com',
      u'creationTime': 1394177224671435L,
      u'expiry': 1461398661,
      u'host': u'.xxx.com',
      u'id': 206439,
      u'inBrowserElement': 0,
      u'isHttpOnly': 0,
      u'isSecure': 0,
      u'lastAccessed': 1398326661001525L,
      u'name': u'...',
      u'path': u'/',
      u'value': u'.394177225'}
    '''
    return connect_db_and_fetchall(db, "moz_cookies");
    
def read_bookmarks(db):
    '''eg
     {u'dateAdded': 1398325606505385L,
      u'fk': 106783,
      u'folder_type': None,
      u'guid': u'SRuT3u4Dqx',
      u'id': 815,
      u'keyword_id': None,
      u'lastModified': 1398325606505385L,
      u'parent': 213,
      u'position': 59,
      u'title': u'title',
      u'type': 1}]
    '''
    return connect_db_and_fetchall(db, "moz_bookmarks") 

def read_bookmarks_roots(db):
    '''eg
    {u'folder_id': 3, u'root_name': u'toolbar'},
    '''
    return connect_db_and_fetchall(db, "moz_bookmarks_roots")

def read_hosts(db):
    '''eg 
     {u'frecency': 2100,
      u'host': u'sqlite.org',
      u'id': 6595,
      u'prefix': None,
      u'typed': 1}]
    '''
    return connect_db_and_fetchall(db, "moz_hosts")

def read_inputhistory(db):
    '''eg
    {u'input': u'sqlite', u'place_id': 10674, u'use_count': 1}]
    '''
    return connect_db_and_fetchall(db, "moz_inputhistory")

def read_keywords(db): 
    '''eg
    {u"id": 0, u"keyword": ""}
    '''
    return connect_db_and_fetchall(db, "moz_keywords")

def read_places(db):
    '''eg 
    {u'favicon_id': 3125,
      u'frecency': 68,
      u'guid': u'l9_8Fu9nOI',
      u'hidden': 0,
      u'id': 100146,
      u'last_visit_date': 1396839928421326L,
      u'rev_host': u'moc.xxx',
      u'title': u'xxx.com title'
      u'typed': 0,
      u'url': u'http://xx.com/index.html',
      u'visit_count': 1},
    '''
    return connect_db_and_fetchall(db, "moz_places")

def read_items_annos(db):
    '''eg: 
    {u'anno_attribute_id': 1,
      u'content': u'....'
      u'dateAdded': 1398325599440828L,
      u'expiration': 4,
      u'flags': 0,
      u'id': 383,
      u'item_id': 814,
      u'lastModified': 1398325599440841L,
      u'mime_type': None,
      u'type': 3}]
    '''
    return connect_db_and_fetchall(db, "moz_items_annos")

def read_annos(db): 
    '''eg:
     {u'anno_attribute_id': 2,
      u'content': u'UTF-8',
      u'dateAdded': 1398325599535283L,
      u'expiration': 4,
      u'flags': 0,
      u'id': 4796,
      u'lastModified': 1398325599535287L,
      u'mime_type': None,
      u'place_id': 106783,
      u'type': 3}]
    '''
    return connect_db_and_fetchall(db, "moz_annos")

def read_anno_attributes(db):
    '''eg:
    {u'id': 15, u'name': u'downloads/metaData'}]
    '''
    return connect_db_and_fetchall(db, "moz_anno_attributes")

def read_historyvisits(db):
    '''eg
    {u'from_visit': 0,
    u'id': 98953,
    u'place_id': 50466,
    u'session': 0,
    u'visit_date': 1382362858694000L,
    u'visit_type': 1}, 
    '''
    return connect_db_and_fetchall(db, "moz_historyvisits")

def print_usage(*args):
    print """mozdb.py tablename db_path 
    cookies.sqlite : cookies,
    formhistory.sqlite : history, 
    places.sqlite : places, bookmarks, bookmarks_roots, hosts, inputhistory, keywords, items_annos, annos, anno_attributes, historyvisits"
    """ 

actions = {
        "cookies": read_cookies,
        "places": read_places,
        "history": read_history,
        "bookmarks": read_bookmarks,
        "bookmarks_roots": read_bookmarks_roots,
        "hosts": read_hosts, 
        "inputhistory": read_inputhistory,
        "keywords": read_keywords, 
        "items_annos": read_items_annos,
        "annos": read_annos,
        "anno_attributes": read_anno_attributes, 
        "historyvisits": read_historyvisits,
        "help": print_usage
        } 

def main(): 
    try:
        arg1 = sys.argv[1]
    except:
        print_usage()
        return
    try:
        arg2 = sys.argv[2] 
    except:
        arg2 = None
    if not os.path.exists(arg1):
        print "%s doesn't exists" % arg1 
    try:
        print json.dumps(actions[arg1](arg2), sort_keys=True, indent=4)
    except KeyError as e: 
        print "unknown option: %s" % arg2 
        print_usage()

if __name__ == "__main__": 
    main()
