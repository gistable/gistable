# $Id: Nielsen2012Python_case.py,v 1.2 2012/09/02 16:55:25 fn Exp $

# Define a url as a Python string (note we are only getting 100 documents)
url = "http://wikilit.referata.com/" + \
    "wiki/Special:Ask/" + \
    "-5B-5BCategory:Publications-5D-5D/" + \
    "-3FHas-20author%3DAuthor(s)/-3FYear/" + \
    "-3FPublished-20in/-3FAbstract/-3FHas-20topic%3DTopic(s)/" + \
    "-3FHas-20domain%3DDomain(s)/" +  \
    "format%3D-20csv/limit%3D-20100/offset%3D0"

# Import the 'urllib' module for Web page retrieval
from urllib import urlopen

# Get help on how to use the module
help('urllib')

# Get and read the web page
doc = urlopen(url).read()  # Object from urlopen has read function

# Show the first 1000 characters
print(doc[:1000])

# Import a CSV reader/writer library. 
# Note: usually you will have all the imports at the top of the Python code.
import csv

web = urlopen(url)
# 'web' is now a file-like handle

lines = csv.reader(web, delimiter=',', quotechar='"')
# 'papers' is now an object that can be iterated over

# Iterate over 'papers'
for line in lines: 
    print(line)


# Each row is of a Python 'list' type
isinstance(line, list) == True
# Or 
type(line) == list


# JSON format instead that Semantic MediaWiki also exports
url_json = "http://wikilit.referata.com/" + \
    "wiki/Special:Ask/" + \
    "-5B-5BCategory:Publications-5D-5D/" + \
    "-3FHas-20author/-3FYear/" + \
    "-3FPublished-20in/-3FAbstract/-3FHas-20topic)/" + \
    "-3FHas-20domain/" +  \
    "format%3D-20json"

# Python module for JSON reading 
import simplejson as json

# Read JSON into a Python structure
response = json.load(urlopen(url_json))

# 'response' is now a hash/dictionary
response.keys()
# Result: ['rows', 'results', 'printrequests']

# response['printrequests'] is a list, map iterates over the list
columns = map(lambda item: item['label'], response['printrequests'])
# gives ['', 'Has author', 'Year', 'Published in', 'Abstract', 
#        'Has topic)', 'Has domain']


# Reread CSV
lines = csv.reader(urlopen(url), delimiter=',', quotechar='"')

# Iterate over 'lines' and insert the into a list of dictionaries
header = []
papers = []
for row in lines:      # csv module lacks unicode support!
    line = [unicode(cell, 'utf-8') for cell in row]
    if not header:     # Read the first line as header
        header = line
        continue   
    papers.append(dict(zip(header, line)))

# 'papers' is now an list of dictionaries

# To get the first abstract:
papers[0]['Abstract']


# Get some natural language processing tools
import nltk

# Get words from first abstract
nltk.word_tokenize(papers[0]['Abstract'])
# Result: [u'Accounts', u'of', u'open', u'source', ...

# Lower case words. 'string' module from Python library
import string
map(string.lower, nltk.word_tokenize(papers[0]['Abstract']))
# Result: [u'accounts', u'of', u'open', u'source'

# Now for all papers
for paper in papers:
    words = map(string.lower, nltk.word_tokenize(paper['Abstract']))
    paper.update({'words': words})


# Double list comprehension
all_words = [ word for paper in papers for word in paper['words'] ]

len(all_words)
# Result: 17059

# Unique words
len(set(all_words))
# Result: 3484

# Count the occurences of all words
wordcounts = dict([ [t, all_words.count(t)] for t in set(all_words) ])

# Another way
wordcounts = {}
for term in all_words:
    wordcounts[term] = wordcounts.get(term, 0) + 1


# Change the ordering of value and key for sorting
items = [(v, k) for k, v in wordcounts.items()]

for count, word in sorted(items, reverse=True)[:5]:
    print("%5d %s" % (count, word))

#  913 the
#  706 of
#  658 ,
#  507 and
#  433 to

# Filter out common words
import nltk.corpus
stopwords = nltk.corpus.stopwords.words('english')

terms = {}
for word, count in wordcounts.iteritems():
    if count > 2 and word not in stopwords and word.isalpha():
        terms[word] = count


# Change the ordering of value and key for sorting
items = [(v, k) for k, v in terms.items()]

for count, word in sorted(items, reverse=True)[:5]:
    print("%5d %s" % (count, word))

#  213 wikipedia
#   64 knowledge
#   64 article
#   54 information
#   50 articles

# Wikipedia is the main topic of all the papers to remove it
terms.pop('wikipedia')

# Convert the dictionary to a list.
terms = list(terms)

# Import of the numerical module
import numpy as np              

# Construct a bag-of-words matrix
M = np.asmatrix(np.zeros([len(papers), len(terms)]))
for n, paper in enumerate(papers):
    for m, term in enumerate(terms):
        M[n,m] = paper['words'].count(term)


# Define a topic mining function (non-negative matrix factorization)
def nmf(M, components=5, iterations=5000):
    # Initialize to matrices
    W = np.asmatrix(np.random.random(([M.shape[0], components])))
    H = np.asmatrix(np.random.random(([components, M.shape[1]])))
    for n in range(0, iterations): 
        H = np.multiply(H, (W.T * M) / (W.T * W * H + 0.001))
        W = np.multiply(W, (M * H.T) / (W * (H * H.T) + 0.001))
        print "%d/%d" % (n, iterations)    # Note 'logging' module
    return (W, H)


# Perform the actual computation
W, H = nmf(M, iterations=50, components=3)

# Show the results in some format
for component in range(W.shape[1]):
    print("="*80)
    print("COMPONENT %d: " % (component,))
    indices = (-H[component,:]).getA1().argsort()
    print(" - ".join([ terms[i] for i in indices[:6] ]))
    print("-")
    indices = (-W[:,component]).getA1().argsort()
    print("\n".join([ papers[i][''] for i in indices[:5] ]))


results = """
================================================================================
COMPONENT 0: 
knowledge - article - information - articles - approach - use
-
Constructing commons in the cultural environment
A systemic and cognitive view on collaborative knowledge building with wikis
Academics and Wikipedia: reframing Web 2.0+as a disruptor of traditional academic power-knowledge arrangements
Addressing gaps in knowledge while reading
Contextual retrieval of single Wikipedia articles to support the reading of academic abstracts
================================================================================
COMPONENT 1: 
web - media - users - content - production - sites
-
A cultural and political economy of Web 2.0
Academics and Wikipedia: reframing Web 2.0+as a disruptor of traditional academic power-knowledge arrangements
Applications of semantic web methodologies and techniques to social networks and social websites
Classifying tags using open content resources
A Wikipedia matching approach to contextual advertising
================================================================================
COMPONENT 2: 
question - classification - answer - systems - answering - method
-
A semantic approach for question classification using WordNet and Wikipedia
A comparison of World Wide Web resources for identifying medical information
Adaptive indexing for content-based search in P2P systems
BinRank: scaling dynamic authority-based search using materialized subgraphs
Classifying tags using open content resources
"""




# Import a graph library and plotting library
import networkx as nx
import matplotlib.pyplot as plt

# Generate coauthor graph
coauthor_graph = nx.Graph()
for paper in papers:
    coauthors = paper['Author(s)'].split(',')
    for n in range(len(coauthors)-1):
        for m in range(n, len(coauthors)):
            coauthor_graph.add_edge(coauthors[n], coauthors[m])

# Extract a subgraph
author_communities = nx.connected_component_subgraphs(coauthor_graph)

# Plot the graph
nx.draw(author_communities[0])
plt.show()


# plt.savefig("coauthorgraph.png")
