import json
import urlparse
from itertools import chain
flatten = chain.from_iterable

from nltk import word_tokenize

from gensim.corpora import Dictionary
from gensim.models.ldamodel import LdaModel
from gensim.models.tfidfmodel import TfidfModel

# from gensim_btm.models import BTGibbsModel

## get bartstrike data

def url_away(tweet):
    string = []
    for word in tweet.split():
        try:
            scheme, netloc, path, params, query, fragment = urlparse.urlparse(word)
        except ValueError:
            continue
        if scheme or netloc:
            pass
        else:
            string.append(path)
    return " ".join(string)
    
def featurize(tweet):
    tweet = tweet.lower()
    tweet = url_away(tweet)
    tokens = word_tokenize(tweet)
    tokens = filter(lambda x: len(x) > 2, tokens)
    return tokens

with open('data/twitter-bart.json', 'r') as f:
    dictionary = Dictionary(featurize(json.loads(line)['text']) for line in f)

class MyCorpus(object):
    def __init__(self, data_file, dictionary):
        self.data_file = data_file
        self.dictionary = dictionary
        
    def __iter__(self):
        with open(self.data_file, 'r') as f:
            for line in f:
                doc = json.loads(line)
                features = featurize(doc['text'])
                yield self.dictionary.doc2bow(features)
        
corpus = MyCorpus("./data/twitter-bart.json", dictionary)

tfidf = TfidfModel(corpus) 
corpus_tfidf = tfidf[corpus]

n_topics = 40
lda = LdaModel(corpus_tfidf, id2word=dictionary, num_topics=n_topics)

#### ------ how to visualize
#### http://tedunderwood.com/2012/11/11/visualizing-topic-models/
#### ------

## word lists
for i in range(0, n_topics):
    temp = lda.show_topic(i, 10)
    terms = []
    for term in temp:
        terms.append(term)
    print "Top 10 terms for topic #" + str(i) + ": "+ ", ".join([i[1] for i in terms])

"""
Top 10 terms for topic #0: expected, rep, announces, over, looks, ktvu, want, like, guys, will
Top 10 terms for topic #1: sfgate, gridlock, normal, happy, head, real, ferries, over, runs, exactly
Top 10 terms for topic #2: a.m., another, vote, members, other, reason, let, pass, ser…, major
Top 10 terms for topic #3: today, killed, sanfranmag, hopes, ave, expect, delays, running, home, train
"""

## word clouds
from os import path
import matplotlib.pyplot as plt
from wordcloud import WordCloud

def terms_to_wordcounts(terms, multiplier=1000):
    return  " ".join([" ".join(int(multiplier*i[0]) * [i[1]]) for i in terms])

wordcloud = WordCloud(font_path="Impact_Label.ttf", background_color="black").generate(terms_to_wordcounts(terms), 1000)

plt.imshow(wordcloud)
plt.axis("off")
plt.savefig("terms1")

plt.close()

## topic-words vectors: topics vs. words
from sklearn.feature_extraction import DictVectorizer

def topics_to_vectorspace(n_topics, n_words=100):
    rows = []
    for i in xrange(n_topics):
        temp = lda.show_topic(i, n_words)
        row = dict(((i[1],i[0]) for i in temp))
        rows.append(row)

    return rows    

vec = DictVectorizer()

X = vec.fit_transform(topics_to_vectorspace(n_topics))
X.shape
# (40, 2457)

## PCA
from sklearn.decomposition import PCA

pca = PCA(n_components=2)

X_pca = pca.fit(X.toarray()).transform(X.toarray())

plt.figure()
for i in xrange(X_pca.shape[0]):
    plt.scatter(X_pca[i, 0], X_pca[i, 1], alpha=.5)
    plt.text(X_pca[i, 0], X_pca[i, 1], s=' ' + str(i))    

plt.title('PCA Topics of Bart Strike Tweets')
plt.savefig("pca_topic")

plt.close()

"""
In [231]:  lda.show_topic(19)
Out[231]: 
[(0.18418766385173357, u'tuesday'),
 (0.10941284772798156, u'over'),
 (0.074073551230934093, u'deal'),
 (0.057823820985690839, u'reached'),
 (0.040004840107066328, u'start'),
 (0.014618710538754369, u'chrisfilippi'),
 (0.01175792963040383, u'commute'),
 (0.010096535268990677, u'buses'),
 (0.0099316408990382157, u'abc7newsbayarea'),
 (0.0089298280179637094, u'late')]

In [232]: lda.show_topic(21)
Out[232]: 
[(0.19463842681026511, u'over'),
 (0.039005911200223162, u'rosenbergmerc'),
 (0.034922463036658115, u'all'),
 (0.029778810358060626, u'thank'),
 (0.018876961986207651, u'unions'),
 (0.018656417067857364, u'hopefully'),
 (0.016893084271683283, u'pissed'),
 (0.013589706807636848, u'someone'),
 (0.012154548491692339, u'per'),
 (0.011787301022370321, u'kron4news')]

In [233]: lda.show_topic(31)
Out[233]: 
[(0.073542501022656165, u'tentative'),
 (0.068444064522636891, u'reach'),
 (0.057170204108103105, u'run'),
 (0.054732038737147118, u'trains'),
 (0.054298622740944123, u'contract'),
 (0.046550628739041838, u'unions'),
 (0.041191568872948219, u'deal'),
 (0.040003874892020903, u'abc7newsbayarea'),
 (0.030594570247699304, u'agreement'),
 (0.025459332467351173, u'announcement')]
"""

X_pca = pca.fit(X.T.toarray()).transform(X.T.toarray())

plt.figure()
for i, n in enumerate(vec.get_feature_names()):
    plt.scatter(X_pca[i, 0], X_pca[i, 1], alpha=.5)
    plt.text(X_pca[i, 0], X_pca[i, 1], s=' ' + n, fontsize=8)
    
plt.title('PCA Words of Bart Strike Tweets')
plt.savefig("pca_words")

plt.close()

## hierarchical clustering
from scipy.cluster.hierarchy import linkage, dendrogram

plt.figure(figsize=(12,6))
R = dendrogram(linkage(X_pca))
plt.savefig("dendro")

plt.close()

## correlation matrix
from scipy.spatial.distance import pdist, squareform

cor = squareform(pdist(X.toarray(), metric="euclidean"))

plt.figure(figsize=(12,6))
R = dendrogram(linkage(cor))
plt.savefig("corr")

plt.close()

## network
import networkx as nx

from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import Normalizer

pca_norm = make_pipeline(PCA(n_components=20), Normalizer(copy=False))

X_pca_norm = pca_norm.fit(X.toarray()).transform(X.toarray())

cor = squareform(pdist(X_pca_norm, metric="euclidean"))

G = nx.Graph()

for i in xrange(cor.shape[0]):
    for j in xrange(cor.shape[1]):
        if i == j:
            G.add_edge(i, j, {"weight":0})
        else:
            G.add_edge(i, j, {"weight":1.0/cor[i,j]})

edges = [(i, j) for i, j, w in G.edges(data=True) if w['weight'] > .8]
edge_weight=dict([((u,v,),int(d['weight'])) for u,v,d in G.edges(data=True)])

#pos = nx.graphviz_layout(G, prog="twopi") # twopi, neato, circo
pos = nx.spring_layout(G)

nx.draw_networkx_nodes(G, pos, node_size=100, alpha=.5)
nx.draw_networkx_edges(G, pos, edgelist=edges, width=1)
#nx.draw_networkx_edge_labels(G, pos ,edge_labels=edge_weight)
nx.draw_networkx_labels(G, pos, font_size=8, font_family='sans-serif')

plt.savefig("network")

plt.close()

