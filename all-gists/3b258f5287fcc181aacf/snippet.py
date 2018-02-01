"""
# App Engine import data from Datastore Backup to localhost

You can use this script to import large(ish) App Engine Datastore backups to your localohst dev server.

## Getting backup files

Follow instructions from Greg Bayer's awesome article to fetch the App Engine backups:
http://gbayer.com/big-data/app-engine-datastore-how-to-efficiently-export-your-data/

Basically, download and configure gsutil and run:
```
gsutil -m cp -R gs://your_bucket_name/your_path /local_target
```

## Reading data to your local (dev_appserver) application

Copy-paste this gist to your Interactive Console, set correct paths and press `Execute`.
(default: http://localhost:8000/console)

"""
from google.appengine.api.files import records
from google.appengine.datastore import entity_pb
from google.net.proto.ProtocolBuffer import ProtocolBufferDecodeError
from google.appengine.datastore import datastore_pbs
from google.appengine.api import datastore
from google.appengine.ext import db
from os.path import isfile
from os.path import join
from os import listdir

def run():
    # Set your downloaded folder's path here (must be readable by dev_appserver)
    mypath = '/local_target'
    # Set your app's name here
    appname = "dev~yourappnamehere"
    
    
    # Do the harlem shake
    onlyfiles = [ f for f in listdir(mypath) if isfile(join(mypath,f)) ]
    ec = datastore_pbs.get_entity_converter()
    
    for file in onlyfiles:
        i = 0
        try:
            raw = open(mypath + "/" + file, 'r')
            reader = records.RecordsReader(raw)
            to_put = list()
            for record in reader:
                entity_proto = entity_pb.EntityProto(contents=record)
                entity_proto.key_.app_ = appname
                entity = db.model_from_protobuf(entity_proto)
                a = db.model_from_protobuf(entity_proto)
    
                for pp in dir(a):
                   try:
                      ppp = getattr(a, "_" + pp)
                      if isinstance(ppp, db.Key):
                         ppp._Key__reference.set_app(appname)
                         ppp
                   except AttributeError:
                      """ It's okay """
                
                to_put.append(a)
                i += 1
                if i % 100 == 0:
                    print "Saved %d %ss" % (i, entity.kind())
                    db.put(to_put)
                    to_put = list()
            
            db.put(to_put)
            to_put = list()
            print "Saved %d" % i
            
        except ProtocolBufferDecodeError:
            """ All good """
 
run()