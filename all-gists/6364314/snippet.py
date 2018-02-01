import sys
try:
	import eventlet
	sys.modules['httplib2'] = eventlet.import_patched('httplib2')
	print "[Optional Import] Using eventlet"
except Exception:
	print "[Optional Import] Not using eventlet"
from semantics3 import Semantics3Request
from semantics3 import Products
from semantics3 import Categories
from semantics3 import Offers
import pprint

api_key    = ""
api_secret = ""
pp = pprint.PrettyPrinter()

products = Products( api_key, api_secret )
products.products_field( "cat_id", 4992 )
products.products_field( "brand", "Toshiba" )
products.products_field( "weight", "gte", 1000000 )
products.products_field( "weight", "lt", 1500000 )
products.products_field( "sitedetails", "name", "newegg.com" )
products.products_field( "sitedetails", "latestoffers", "currency", "USD" )
products.products_field( "sitedetails", "latestoffers", "price", "gte", 100 )
products.cache(5)

for i in products.iter():
	pass
# Build the query

products.categories_field( "cat_id", 4992 );

# Execute the query
results = products.get_categories();

# View the results of the query



products.offers_field( "sem3_id", "4znupRCkN6w2Q4Ke4s6sUC");
products.offers_field( "seller", ["LFleurs","Frys","Walmart"] );
products.offers_field( "currency", "USD");
products.offers_field( "price", "gte", 30);
products.offers_field( "lastrecorded_at", "gte", 1348654600);

results = products.get_offers()

pp.pprint(results)
