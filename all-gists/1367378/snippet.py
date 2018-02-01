#!/usr/bin/env python 

# This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 
#    Author: Daniel Riegel


import sys
import pymongo
import time
import getopt
import copy
from pymongo import Connection
from pymongo.database import Database
from datetime import datetime, timedelta
from locale import atoi
import random
import math
import threading
import logging

from Queue import Queue

def get_mongo_db(host):
    connection = Connection(host,
        port=27017)
    db = Database(connection, "atest")
    db.set_profiling_level(0)
    return db

def generate_uuids(num, length=6):
    results = []	
    for i in range(num):
        val = random.randint(0,2**(length*8))
        results.append("%x" % val) 
    return results

def generate_and_insert_ids(coll, doc_template, num_docs, prepad, associative, logger):
    logger.debug("Starting uuid generation and insertion")
    uuids = generate_uuids(num_docs)
    
    start = time.time()
    for uuid in uuids:
        doc_template["uuid"] = uuid
        coll.insert(doc_template, None, safe=False)
        if prepad:
            coll.update({"uuid" : uuid} ,{ "$set" : { "logs" : [] }})
        if associative:
            coll.update({"uuid" : uuid} ,{ "$set" : { "logs" : {} }})

    logger.debug("done inserting initial documents: %s ms\n" % ((time.time() - start) * 1000))
    return uuids

class DBUpdater(threading.Thread):
    def __init__(self, collection_name, queue, host):
        self.queue = queue
        threading.Thread.__init__(self)
        self.db = get_mongo_db(host)
        self.coll = self.db[collection_name]
        self.daemon = True
        
    def stop(self):
        self.queue.put(None)
        
    def run(self): 
        while True:
            args = self.queue.get(True)
            if args == None:
                break
#            self.coll.find(args[0])[0]  # just to warm the cache, don't think we need it
            self.coll.update(args[0], args[1], upsert=args[2], safe=args[3])


def run_test(num_docs = 100, 
             list_length = 1000,
             entry_size =  300,
             prepad = False,
             in_place = False,
             safe_write = False,
             associative = False,
             group_sub_list = 0,
             num_threads = 2,
             verbose = False,
             host = "localhost"):
    
    #settings / constants
    
    time_buckets = 15
    outer_loop_delay_ms = 100
    inner_loop_delay_ms = 0
    logger = logging.Logger(__name__)
    handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(handler)
    if verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    # locals 
    
    filler = "x" * entry_size
    padding = []
    dt = datetime.today()
    db = get_mongo_db(host)

    args = """num_docs: %d
array_element_size: %d
list_length: %d
prepad: %s
in_place: %s
safe_write: %s
associative: %s
group_sub_list: %d
num_threads: %d
    """ % (num_docs, 
           entry_size,
           list_length, 
           prepad,
           in_place,
           safe_write,
           associative,
           group_sub_list,
           num_threads )

    # argument processing
    
    if group_sub_list == 0:
        group_sub_list = list_length
    if in_place:
        padding = map( lambda f : filler, range(list_length))
    elif prepad:
        padding = "x" * (list_length * entry_size)
    elif group_sub_list < list_length:
        padding = {}
        for hr in range(int(math.ceil(list_length / group_sub_list))):
            padding["%d" % hr] = {"hr" : hr, "vals": [] }

    doc_template = { 
                   "day" : dt.day, 
                   "month" : dt.month, 
                   "year" : dt.year,
                   "logs" : padding,
                   }

    # loop variables
    
    counter = 0
    dbwait_table = 0    
    times = []
    coll = db.arraytest
    time_div = float(list_length) / time_buckets
    start = time.time()
    
    # start doing something
    
    coll.drop() # clean it out
    coll.ensure_index([("uuid",pymongo.ASCENDING)])
    uuids = generate_and_insert_ids(coll, 
                                    doc_template, 
                                    num_docs, 
                                    prepad, 
                                    associative,
                                    logger)
        
    oldidx = 0
    i = 0
    max_i = list_length * num_docs
    update_start = time.time()
    
    update_queue = Queue(num_threads * 2)
    updaters = []
    
    for j in range(num_threads):
        updaters.append(DBUpdater("arraytest", update_queue, host))
        updaters[j].start()
        j += 1
    
    while counter < list_length:
        t1 = time.time()
    	idx = int(math.floor( i * time_buckets / max_i))
        sublist_idx = counter / group_sub_list
        if oldidx < idx:
            logger.debug("\n%d of %d (%d of %d updates)" % ( idx + 1, time_buckets, i, max_i))
            oldidx = idx
        for uuid in uuids:
                upsert_dict = {"$push" : { "logs" : filler }}
                query = { "uuid" : uuid }
                
                if group_sub_list < list_length:
                    query = {"uuid" : uuid }
                    upsert_dict = {"$push" : {"logs.%d.vals" % sublist_idx : filler }}
                if associative:
                    upsert_dict = {"$set" : {"logs.%d" % counter : filler }}
                if in_place:
                    upsert_dict = {"$set" : {"logs.%d" % counter : filler }}
                if group_sub_list == 1:
                    # just insert, no updates
                    doc_template["uuid"] =  uuid + "%d" % counter
                    doc_template["logs"] = filler 
                    coll.insert(doc_template)
                else:
                    update_queue.put( [query, upsert_dict, True, safe_write], True)
                    
                if verbose and (i % 100 == 0):
                    sys.stdout.write(".")
                    sys.stdout.flush()
                i += 1 
                time.sleep(inner_loop_delay_ms / 1000)
                
        insert_time = time.time() - t1
        
        if len(times) <= idx:
            times.append(0)
        times[idx] += insert_time * 1000 / time_div / num_docs
        counter += 1
        time.sleep(outer_loop_delay_ms / 1000)

    # shut down worker threads
    logger.debug("stopping threads...")
    for updater_thread in updaters:
        updater_thread.stop()
    
    logger.debug("joining threads...")
    for updater_thread in updaters:    
        updater_thread.join()
    
    logger.info("updates took %d ms" % ((time.time() - update_start)*1000))
    print args
    for i, timey in enumerate(times):
        logger.info("%d: %f" % (i, timey))
    
    return times


def expand_array(arglist):
    i = 0
    result = []
    for arg in arglist:
        if type(arg) == list:
            results = []
            for val in arg:
                subarg = copy.deepcopy(arglist)
                subarg[i] = val
                results.extend(expand_dict(subarg))
            return results
        else:
            result.append(arg)
        i += 1         
    return [result]
    
def expand_dict(target):
    i = 0
    result = {}
    for key, val in target.iteritems():
        if type(val) == list:
            results = []
            for subval in val:
                # split it into one dict for each value in the array and recurse
                target_clone = copy.deepcopy(target)
                target_clone[key] = subval
                results.extend(expand_dict(target_clone))
            return results
        else:
            result[key] = val
        i += 1         
    return [result]

def usage():
    print """
NAME
    %s - measure mongo $push performance on arrays of a set size for a specified collection size 

SYNOPSIS
    %s: [ OPTIONS ]

DESCRIPTION
    Run a test of a mongo database with a variety of parameters.  Allows simple comparison of 
    different parameter values.  If multiple parameters are passed in for any arguments, 
    run multiple tests on the cross product of all possible combinations and print out a 
    summary of the results on completion.
     
    -a, --associative  { y | n | yn | y,n }     default False
        add entries as key - value pairs under the logs field instead of pushing then onto an array 

    -g --group_sub_list=sub_list_size
        place entries in multiple lists under hash keys. List length is limited to sub_list_size.

    -h, --help
        print this usage info
        
    -o, --host
        mongodb host name or ip

    -i, --in_place  { y | n | yn | y,n }     default False
        create the entire document at the start, and simply $set the values in the loop
        not compatible with -a

    -l, --list_length=length      default 1000  
        how many entries to add to the list in each document
         
    -n, --num_docs=num         default 100  
        total number of independent documents to create and fill
        
    -p, --prepad  { y | n | yn | y,n }     default False
        create documents with their ultimate size from the start, then immediately delete the padding 
        
    -s, --entry_size=size         default 300
        the size, in bytes, of each entry in the arrays.  It is just a string of 'x' characters

    -t, --num_threads=num              default 2
        the number of threads to use to update
    
    -v, --verbose
        print verbose info to console

    -w, --safe_write  { y | n | yn | y,n }     default False
        use the safe write flag (safe = True) for all updates and inserts
        
    """ % (__file__, __file__)
    
def main():
    
    dt = datetime.today() # - timedelta(days=5)

    argv = sys.argv


# if this fails, add this to the environment:
#  export PYTHONPATH=$PYTHONPATH:..  (or wherever ears_tools is

    try:
        opts, args = getopt.getopt(argv[1:], "hn:l:s:p:i:w:a:g:t:o:v", ["help", 
                                                              "num_docs=",
                                                              "list_length=",
                                                              "entry_size=",
                                                              "prepad=",
                                                              "in_place=",
                                                              "safe_write=",
                                                              "associative=",
                                                              "group_sub_list=",
                                                              "num_threads=",
                                                              "host="
                                                              "verbose",
                                                              ])

    except getopt.GetoptError:
        usage()
        sys.exit(2)

    args = { "num_docs" : 100, 
            "list_length" : 1000,
            "entry_size" : 300,
            "prepad" : False,
            "in_place" : False,
            "safe_write" : False,
            "associative" : False,
            "group_sub_list" : 0,
            "num_threads" : 2,
            "verbose" : False,
            "host" : "localhost"
            }
    
    bool_map = { "y" : True, "n" : False, "yn" : [True,False], "y,n" : [True,False] } 
    
    try :
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                #TODO write usage
                usage()
                sys.exit()
            elif opt in ("-n", "--num_docs"):
                args["num_docs"] = map( lambda x : atoi(x), arg.split(","))
            elif opt in ("-l", "--list_length"):
                args["list_length"] = map( lambda x : atoi(x), arg.split(","))
            elif opt in ("-s", "--entry_size"):
                args["entry_size"] = map( lambda x : atoi(x), arg.split(","))
            elif opt in ("-p", "--prepad"):
                args["prepad"] = bool_map.get(arg, "True")
            elif opt in ("-i", "--in_place"):
                args["in_place"] = bool_map.get(arg, "True")
            elif opt in ("-w", "--safe_write"):
                args["safe_write"] = bool_map.get(arg, "True")
            elif opt in ("-a", "--associative"):
                args["associative"] = bool_map.get(arg, "True")
            elif opt in ("-g", "--group_sub_list"):
                args["group_sub_list"] = map( lambda x : atoi(x), arg.split(","))
            elif opt in ("-o", "--host"):
                args["host"] = arg
            elif opt in ("-t", "--num_threads"):
                args["num_threads"] = map( lambda x : atoi(x), arg.split(","))
            elif opt in ("-v", "--verbose"):
                args["verbose"] = True
            
    except Exception:
        usage()
        sys.exit(2)

    argsetlist = expand_dict(args)
    print "Running %d times, with the following argument sets: " % len(argsetlist)
    for i, argset in enumerate(argsetlist):
        print "%d: %r" % (i,argset)
        
#    sys.exit(0)
    
    times = []
    for argset in argsetlist:
        print "now running %r" % argset
        times.append(run_test(**argset))
    
#    print "\t".join(map(lambda x : "%r" % x,argsetlist))
    for i, run in enumerate(argsetlist):
        print "run #%d: %r" % (i, run)
    print "Average time per insert operation, in ms"
    for i, row in enumerate(zip(*times)):
        
        print "%d:\t%r" % (i, row)


if __name__ == "__main__":
    main()



