#!/bin/python
import elasticsearch
import sys, getopt

def main(argv):
   number = 10
   search = 'metrics.changes.total:0 AND type:puppet-report'
   try:
      opts, args = getopt.getopt(argv,"hs:n:",["search=","number="])
   except getopt.GetoptError:
      print 'delete_from_elasticsearch.py -s <search_expression> -n <number_per_shard>'
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print 'delete_from_elasticsearch.py -s <search_expression> -n <number_per_shard>'
         sys.exit()
      elif opt in ("-s", "--search"):
         search = arg
      elif opt in ("-n", "--number"):
         number = arg
   print 'I will search for "', search
   print 'I will delete these in batches of "', number
   delete_docs(search, number)

def delete_docs(search, number=10):   
  
  # Setup elasticsearch connection. 
  es = elasticsearch.Elasticsearch(
    ['localhost'],
    # sniff before doing anything
    sniff_on_start=True,
    # refresh nodes after a node fails to respond
    sniff_on_connection_fail=True,
    # and also every 60 seconds
    sniffer_timeout=60
  )
  
  # Start the initial search. 
  hits=es.search(
    q=search,
    index="*logstash-*",
    fields="_id",
    size=number,
    search_type="scan",
    scroll='5m',
  )
  
  # Now remove the results. 
  while True:
    try: 
      # Git the next page of results. 
      scroll=es.scroll( scroll_id=hits['_scroll_id'], scroll='5m', )
    except elasticsearch.exceptions.NotFoundError: 
      break 
    
    # We have results initialize the bulk variable. 
    bulk = ""
    
    # Remove the variables. 
    for result in scroll['hits']['hits']:
      bulk = bulk + '{ "delete" : { "_index" : "' + str(result['_index']) + '", "_type" : "' + str(result['_type']) + '", "_id" : "' + str(result['_id']) + '" } }\n'
#    print "Items left " + str(scroll['hits']['total']) + ' deleting ' + str(bulk.count('delete')) + ' items.'
#    print bulk 
    es.bulk( body=bulk )


if __name__ == "__main__":
   main(sys.argv[1:])