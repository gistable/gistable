#!/usr/bin/env python      

# Written with pymongo-3.3

author__ = 'mongolab'                                                                                                \
 
 
import pymongo
import sys, datetime, time
import random
 
URI = "mongodb://testdbuser:testdbpass@flip.mongolab.com:53117,flop.mongolab.com:54117/testdb?replicaSet=rs-flip-flop"
RETRY_WAIT_IN_SEC = 3
 
###############################################################################                                        \
                                                                                                                        
def main(args):
 
    client = pymongo.MongoReplicaSetClient(URI)
    db = client.get_default_database()
 
    collection_name = _get_unique_tmp_collection_name()
    c = db[collection_name]
 
    try:
        while True:
 
            now = datetime.datetime.now()
            try:
                if client.primary:
                    print ("%s: connected to primary server '%s'..."
                           % (now, client.primary[0] + ":" + str(client.primary[1])))
 
                print("...about to perform safe insert.")
                c.insert({ "t" : now })
 
                print("...about to read.")
 
                num_docs = c.find({}).count()
                print ("...successfully inserted & read. There are %i "
                       "documents in your temporary test collection."
                       % num_docs)
 
                retry_total_time = 0
            except Exception as e:
                print ("*** EXCEPTION - %s" % e)
                print ("*** ...will sleep for %s seconds before retrying "
                       "[total of %s seconds]"
                       % (RETRY_WAIT_IN_SEC, retry_total_time))
                retry_total_time += RETRY_WAIT_IN_SEC
 
            print ("\n")
            time.sleep(RETRY_WAIT_IN_SEC)
 
    except:
        print ("An unexpected exception occurred. Performing cleanup "
               "if possible by dropping test collection '%s'..."
               % collection_name)
        c.drop()
        client.close() 

###############################################################################                                        \
                                                                                                                        
def _get_unique_tmp_collection_name():
    return "collection%s" % (random.randint(0, 99999999))
 
###############################################################################                                        \
                                                                                                                        
if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except SystemExit as e:
        if e.code == 0:
            pass
    except Exception as e:
        print ("*** EXCEPTION - %s" % str(e))
        print ("    ... please try connecting again in 10 seconds, a "
               "failover is probably in progress right now. If you still "
               "can't connect, please email support@mongolab.com for help. "
               "Thank you!")