# Script to generate a co-occurring tag graph from news articles via Guardian Platform API
# This is a quick hack script - just get things done... Needs refactoring/tidying...

import simplejson,urllib,csv,sys
from itertools import combinations

# D3.js json generator from https://bitbucket.org/hagberg/networkx-d3
import d3


import networkx as nx

# A New York Times  API key will be required...
APIKEY_NYT=''

# accept a search phrase; this will be quoted in the actual search...
try:
	terms=sys.argv[1:]
except:
	exit(-1)

# Create a filename that captures the search phrase
fnx='nyt-'+'_'.join(terms)
print 'Using',fnx

# Build up the search phrase for the Guardian Platfrom API
term='"'+' '.join(terms)+'"'
enc=urllib.urlencode({'query':term})
print '...'+term+'...',enc

# We'll use NetworkX to construct a graph for the tag-tag network
G=nx.Graph()

# Generate the URL needed to call the New York Times Article API
# At the moment the start date and the page number is hardwired
# Need to tweak this to look at total number of results and page through them
nyturl='http://api.nytimes.com/svc/search/v1/article?'+enc+'&fields=des_facet,title,url&api-key='+APIKEY_NYT

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

# Call the API
dr=[]
page=0
more=True
while page<5 and more==True:
	nytpurl=nyturl+'&offset='+str(page)
	tmpdata = simplejson.load(urllib.urlopen(nytpurl))
	page=page+1
	if tmpdata['total'] < page*10: more=False
	for r in tmpdata['results']: dr.append(r)


# This is a reminder that the results aren't paged (yet!) and you just get the most recent 50

edges=[]
edges2=[]
nodes={}
nodes2={}

# For each article in the results set:
for result in dr:
	# Collect a list of tags associated with the current article
	tags=[]
	if 'des_facet' in result:
		taglist=result['des_facet']
		# Build up a list of unique node IDs, firstly using article IDs for the article-tag graph
		if result['url'] not in nodes:
			nodes[result['url']]=( result['url'],result["title"].encode('utf-8') )
		# Now handle the article tags
		for tag in taglist:
			print result['url'],tag,tag
			edges.append((result['url'],tag))
			# Build up a list of tags associated with this article
			tags.append(tag)
			# Add the tags to the unique list of node IDs
			if tag not in nodes:
				nodes[tag]= ( tag, tag)
				nodes2[tag]= ( tag, tag )
				G.add_node(tag,label=tag)
		# For the tag-tag graph, we need to list the various tag combinations for this article
		combos=map(list, combinations(tags, 2))
		for c in combos:
			edges2.append((c[0],c[1]))
			G.add_edge(c[0],c[1])

#I originally had a clunky recipe for outputting Gephi gdf files.
#As we have networkx loaded and representing the graph it much easy to write files directly:
#filepathandname='something Appropriate'
#nx.write_graphml(G, filepathandname+".graphml")
#edgelist (eg for use in R)
#nx.write_edgelist(G, filepathandname+".txt",data=False)

# Here's the clunky way of printing out the article-tag nodelist
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

d3.draw_force(G,'force/force.json')