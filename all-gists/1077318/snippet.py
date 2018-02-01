#Sample PLOS api code for use with python Solr library Sunburnt
#( https://github.com/tow/sunburnt )
#!Note! requires sunburnt's external libraries: httplib2,lxml 
#https://groups.google.com/d/topic/plos-api-developers/zv591sFz6TM/discussion

import sunburnt,urllib2
class PlosInterface(sunburnt.SolrInterface):
    def __init__(self,api_key):
        plos_url = "http://api.plos.org/search"
        #either
	plos_schema  = urllib2.urlopen("http://api.plos.org/search-examples/schema.xml")
	#or (be polite, use stored file instead of urlopen)
	#plos_schema = open('/home/dbuschho/workspace/publication_timeline/plos_schema.xml')
						#localfile handle open('../plos_schema.xml') from
                                                #http://api.plos.org/search-examples/schema.xml
        #Python base class magic ... make this class a SolrInterface like object
        #note that schemadoc if requested by url will be loaded                                      
        super(PlosInterface, self).__init__(url=plos_url,schemadoc=plos_schema)
        #Replace default connection with one that 
        self.conn = PlosInterface.PlosConnection(url=plos_url,api_key=api_key)    
    
    #Create specific PlosConnection subclass of SolrConnection
    #to force addition of API_KEY query param to all queries
    #(defined within PlosInterface class to keep namespace clean)
    class PlosConnection(sunburnt.sunburnt.SolrConnection):
        api_key = None
        def __init__(self, url, api_key):
            self.api_key = api_key
            super(PlosInterface.PlosConnection, self).__init__(url=url)
        def select(self, params):
            params.append((u'api_key',self.api_key))
            return sunburnt.sunburnt.SolrConnection.select(self,params)



#Actual test code
if __name__ == '__main__':
    plos_interface = PlosInterface(api_key=u'1234567')
    
    count   = 0 #Count number of results printed
    start   = 0
    rows    =10
    
    while True:
        results = plos_interface.query(title=u'Chemistry').paginate(start,rows).execute()
                            #handle while loop bookkeeping
        start += rows       #increment query loop
        
	if(not results):    #stop loop if no more results
            break           #see http://stackoverflow.com/questions/6631128
        
        #Actually do something with data received
        for result in results:
            print result
            count += 1
        
    print count