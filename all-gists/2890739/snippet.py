import urllib
import settings
try:
	import json
except ImportError:
	import simplejson as json


class YahooException(Exception): 
	pass 


class YahooGeocoder(object): 

	@classmethod 
	def geocode(self, query): 
		file = urllib.urlopen("http://where.yahooapis.com/geocode?%s" % 
			urllib.urlencode({ 
				'appid': settings.YAHOO_APP_ID, 
				'flags': 'j', 
				'q': query 
			})) 
		try: 
			result = json.loads(file.read()) 
			return result['ResultSet']['Results'] 
		except: 
			print result
			raise YahooException(result['ResultSet']['ErrorMessage']) 
		finally: 
			file.close() 
		

if __name__ == "__main__":
    import sys
    from optparse import OptionParser
    
    def main():
        """
        Geocodes a location given on the command line.
        
        Usage:
            yahoogeocoder.py "1600 amphitheatre mountain view ca"
        """
        usage = "usage: %prog [options] address"
        parser = OptionParser(usage)
        (options, args) = parser.parse_args()
        
        if len(args) != 1:
            parser.print_usage()
            sys.exit(1)
        
        query = args[0]
        gcoder = YahooGeocoder()
        
        try:
            results = gcoder.geocode(query)
        except YahooException, err:
            sys.stderr.write('%s\n%s\nResponse:\n' % (err.url, err))
            json.dump(err.response, sys.stderr, indent=4)
            sys.exit(1)
        
        result = results[0]
        print result
        print (float(result['latitude']), float(result['longitude']))

    main()