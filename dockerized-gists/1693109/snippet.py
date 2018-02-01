"""

Created on Fri Jan 27 21:48:58 2012
@author: jay
"""
    
import json
import os
import gdbm
import time
import pickle
    
def main():
    directory = '/home/jay/.mozilla/firefox/qyrgphtu.default/bookmarkbackups'
    if not os.path.isdir(directory):
        return
    for path, dirs, files in os.walk(directory):
        if path == directory:
            break
    files = sorted(files)
    filename = files[-1]
    Path = os.path.join(directory, filename)
    f=open(Path,'r')
    con = json.load(f)
    f.close()
        
    # Get Bookmarks Menu / Bookmarks toolbar / Tags / Unsorted Bookmarks
    f = gdbm.open('bookmark_json','c')
    con_list = con['children'] # this list will have all of the above mentioned things
    
    for i in range(len(con_list)):
        con_sub_list = con_list[i]['children']  # Access them individually
        for tags in con_sub_list:
            if tags.has_key('children'): # Accessing Tags # get tag list
                bookmarks = tags['children'] # get all the bookmarks corresponding to the tag
                if bookmarks:
                    for bookmark in bookmarks: # Access each bookmark
                        Tag = tags['title']
                        uri = bookmark['uri']
                        title = bookmark['title']
                        dateAdded =  bookmark['dateAdded'] # it gives a long int eg. 1326378576503359L
                        add_date = dateAdded/1000000  # The output of time.time() would be 1326378576.503359
                        lastModified = bookmark['lastModified']
                        modified_date = lastModified/1000000
                        f[uri] = pickle.dumps((title, Tag, add_date, modified_date))
            else:
                if (tags['title'] != 'Recently Bookmarked' 
                    and tags['title'] != 'Recent Tags' 
                    and tags['title'] != 'Most Visited'
                    and con_list[i]['title'] != 'Bookmarks Menu'):
                     # Accessing Unsorted Bookmarks
                     Tag = con_list[i]['title']
                     title = tags['title']
                     uri = tags['uri']                      
                     dateAdded =  tags['dateAdded']
                     add_date = dateAdded/1000000
                     lastModified = tags['lastModified']
                     modified_date = lastModified/1000000                                           
                     f[uri] = pickle.dumps((title, Tag, add_date, modified_date))
    f.close()
if __name__ == '__main__':
    main()