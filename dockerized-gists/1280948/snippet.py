# Script to generate a co-occurring tag graph from news articles via Guardian Platform API
# This is a quick hack script - just get things done... Needs refactoring/tidying...

import simplejson,urllib,csv,sys
from itertools import combinations

# A Guardian Platfrom API key will be required...
APIKEY=''

# accept a search phrase; this will be quoted in the actual search...
try:
	terms=sys.argv[1:]
except:
	exit(-1)

# Create a filename that captures the search phrase
fnx='_'.join(terms)
print 'Using',fnx

# Build up the search phrase for the Guardian Platfrom API
term='"'+' '.join(terms)+'"'
enc=urllib.urlencode({'q':term})
print '...'+term+'...',enc


# Generate the URL needed to call the Guardian Platform API
# At the moment the start date and the page number is hardwired
# Need to tweak this to look at total number of results and page through them
gurl='http://content.guardianapis.com/search?' + enc + '&from-date=2011-01-01&page-size=50&format=json&show-tags=keyword&ids=type%2Farticle&api-key='+APIKEY


# We're going to write a couple of Gephi files:

# The first file is a bipartite graph from article to tag
# That is: look up the articles that mention the search phrase,
# then plot a graph of articleID-tag for each tag
f=open(fnx+'.gdf','wb')
writer = csv.writer(f)

# The second file directly links tags to the tags they co-occur with.
# That is, for each article, plot the tags associated with the article and edges between them.
f2=open(fnx+'2.gdf','wb')
writer2 = csv.writer(f2)

# Call the Guardian Platform API
data = simplejson.load(urllib.urlopen(gurl))

# This is a reminder that the results aren't paged (yet!) and you just get the most recent 50
if data['response']['total']>50: print "more if you want 'em for",term

dr=data['response']['results']
edges=[]
edges2=[]
nodes={}
nodes2={}

# For each article in the results set:
for result in dr:
	# Collect a list of tags associated with the current article
	tags=[]
	# Build up a list of unique node IDs, firstly using article IDs for the article-tag graph
	if result['id'] not in nodes:
		nodes[result['id']]=( result['id'],result["webTitle"].encode('utf-8') )
	# Now handle the article tags
	for tag in result['tags']:
		print result['id'],tag['id'],tag['webTitle']
		edges.append((result['id'],tag['id']))
		# Build up a list of tags associated with this article
		tags.append(tag['id'])
		# Add the tags to the unique list of node IDs
		if tag['id'] not in nodes:
			nodes[tag['id']]= ( tag['id'], tag['webTitle'] )
			nodes2[tag['id']]= ( tag['id'], tag['webTitle'] )
	# For the tag-tag graph, we need to list the various tag combinations for this article
	combos=map(list, combinations(tags, 2))
	for c in combos:
		edges2.append((c[0],c[1]))

# Print out the article-tag nodelist
writer.writerow(['nodedef>name VARCHAR','label VARCHAR'])
for node in nodes:
	n1,n2=nodes[node]
	writer.writerow([ n1,n2 ])

# Print out the tag-tag nodelist
writer2.writerow(['nodedef>name VARCHAR','label VARCHAR'])
for node in nodes2:
	n1,n2=nodes[node]
	writer2.writerow([ n1, n2 ])

# Print out the article-tag edgelist
writer.writerow(['edgedef>from VARCHAR','to VARCHAR'])
for e1,e2 in edges:
	writer.writerow([ e1, e2 ])

# Print out the tag-tag edgelist
writer2.writerow(['edgedef>from VARCHAR','to VARCHAR'])
for e1,e2 in edges2:
	writer2.writerow([ e1, e2 ])

# Tidy up...	
f.close()
f2.close()