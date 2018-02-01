import urllib2, simplejson

# Hier de respons van de website als je de query opent.
response = simplejson.dumps(urllib2.urlopen("http://search.twitter.com/search.json?geocode=51.985263,5.663259,5km&q=forum").readline())

# Format de website zo dat python het kan lezen als python objecten ipv JSON
# de 5 en de 1 slaan op de indexing van de response. Het 5e item zijn de tweets zelf in deze request, kan misschien verschillen per search.
loadaspy = simplejson.loads(simplejson.loads(response)).items()[4][1]
