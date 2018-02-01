import itertools
import requests, lxml, lxml.html
import json
# 7603 Hard Drives
# 7611 RAM
# 6642 random store

def newegg_stores_req():
    r = requests.api.get('http://www.ows.newegg.com/Stores.egg/Menus')
    return [store['StoreID'] for store in json.loads(r.content)]

def newegg_categories_req(store_id):
    r = requests.api.get(
      'http://www.ows.newegg.com/Stores.egg/Categories/%i' % store_id)
    return [cat['NodeId'] for cat in json.loads(r.content)]

def newegg_items_page_req(node, page):
    r = requests.api.post(
      'http://www.ows.newegg.com/Search.egg/Advanced', 
      json.dumps({'NodeId':node, 'PageNumber':page})
    )
      #'''{"NodeId":6642,"PageNumber":%i}''' % page)
    
    prodlist = json.loads(r.content)['ProductListItems']
    if prodlist is None: return False
    
    items = [
      (item['Title'], float(item['OriginalPrice'][1:].replace(',', ''))) 
      for item in prodlist
    ]

    return items

def newegg_items(node):
    last_res = list()
    page = 0
    while last_res != False:
        yield last_res
        page += 1
        last_res = newegg_items_page_req(node, page)

def checkpoint(items):
    with open('checkpoint.json', 'w') as f:
        json.dump(items, f, indent=2)

def allitems(nodes):
    items = list()
    for node in nodes:
        checkpoint(items)
        for page in newegg_items(node):
            items += page
            checkpoint(items)
    checkpoint(items)

nodes = list(itertools.chain(
    *[newegg_categories_req(store) for store in newegg_stores_req()]
))

items = allitems(nodes)

for name, price in items:
    print name[:20], price
