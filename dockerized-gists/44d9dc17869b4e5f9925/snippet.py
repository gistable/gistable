#! /usr/bin/env python
import os
import os.path
import stat 
import sys 

def new_queue(): 
    #the dummy head
    h =  {
            "item": None,
            "prev": None,
            "next": None
            }
    h["prev"] = h;
    h["next"] = h;
    return h


def queue_put(h,  item): 
    p = h["prev"]
    node = {
            "item": item,
            "prev": p,
            "next": h
            }  
    p["next"] = node
    h["prev"] = node

def queue_get(h): 
    if h["next"] == h:
        return 
    p = h["next"]
    h["next"] = p["next"]
    h["next"]["prev"] = h
    return p["item"] 


def queue_isempty(h):
    if h["next"] == h:
        return True
    else:
        return False


def travfs_level_order(d): 
    if d.startswith("."):
        return
    s = [] 
    q = new_queue()
    queue_put(q, d) 
    while not queue_isempty(q): 
        fi = queue_get(q)
        try:
            st = os.stat(fi)
        except: 
            continue
        if stat.S_ISDIR(st.st_mode):
                s.append((fi, st.st_size)) 
                try:
                    sub = os.listdir(fi)
                except:
                    continue
                for i in sub:
                    queue_put(q, os.path.join(fi, i))
        else: 
            try:
                size = os.stat(fi).st_size
            except:
                continue
            s.append((fi, size))
    return s



K = 1024
M = K * K
G = M * K


def pretty_size(size):
    if size / G:
        return str(size / G) + "G"
    elif size / M:
        return str(size / M) + "M"
    elif size / K:
        return str(size / K) + "K"
    else:
        return str(size) + "B"


def sort_files(s):
    s.sort(key = lambda x: x[1], reverse=True)


def top_k_size(files, k):
    of = "{:<10}{:<20}"
    for i in range(k): 
        try:
            fi = files[i]
        except:
            break
        print of.format(pretty_size(fi[1]), fi[0]) 


def print_usage():
    print "python travfs.py path n\nfind the top n biggest file in a path"


if __name__ == "__main__": 
    vlen = len(sys.argv)
    if vlen == 2: 
        path = sys.argv[1]
        k = 10
    elif vlen == 3:
        path = sys.argv[1] 
        k = int(sys.argv[2])
    else:
        print_usage()
        exit()
    files = travfs_level_order(os.path.abspath(path)) 
    sort_files(files)
    top_k_size(files, k) 