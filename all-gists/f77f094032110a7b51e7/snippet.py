#-*- coding: utf-8 -*-
import sys
import os
import pprint

import internetarchive

def _search_collection(collection_name):
    """ Searches the internet archive for the specified collection.
    if no items are found for the collection it returns None otherwise
    the Search object is returned.
    """
    collection = internetarchive.search_items('collection:{}'.format(collection_name))
    if collection.num_found == 0:
        return None
    else:
        return collection

def _get_item_data(item):
    data = internetarchive.get_item(item.get('identifier'))
    original_size = 0
    total_size    = 0
    for f in data.files:
        total_size += int(f.get('size',0))
        if f['source'] == 'original':
            if f['name'].endswith('_files.xml'):
                xml_file = data.get_file(data.identifier + '_files.xml')
                xml_file.download()
                size = os.path.getsize(data.identifier + '_files.xml')
                os.remove(data.identifier + '_files.xml')
                original_size += size
                total_size    += size
            else:
                original_size += int(f.get('size',0))

    return total_size,original_size

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Missing parameter: collection name')
        sys.exit(-1)

    collection = sys.argv[1]
    print('Getting data for the collection {}'.format(collection))

    collection_data = _search_collection(collection)
    if not collection:
        print('No collection {} found'.format(collection))
        sys.exit(-1)
    else:
        num_items = collection_data.num_found
        print('Found {} items in the collection {}'.format(num_items, collection))
        proccessed = 1
        # Note the internetarchive library does a http request for each item so this
        # could take some time.
        collection_original_size = 0
        collection_total_size    = 0
        for item in collection_data:
            print('[{}/{}] Processing item {}'.format(proccessed, num_items, item['identifier']))
            proccessed += 1
            t,o = _get_item_data(item)
            collection_original_size += o
            collection_total_size    += t
        print('Total collection file size:          {}'.format(collection_total_size))
        print('Total collection original file size: {}'.format(collection_original_size))
