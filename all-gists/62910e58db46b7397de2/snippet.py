from urllib2 import urlopen
from json import load 
import re, nltk
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import wordnet, stopwords
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', 
    level=logging.INFO)
from gensim import corpora, models, similarities, matutils
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
 
url = 'http://api.npr.org/query?apiKey=' 
key = 'API_KEY'
url = url + key
url += '&numResults=50&format=json&id=1001'
url += '&requiredAssets=text'
 
response = urlopen(url)
json_obj = load(response)
 
with open('nprarticles.txt','w') as f:
    for story in json_obj['list']['story']:
        article = []
        for paragraph in story['textWithHtml']['paragraph']:
            article.append(paragraph['$text'])
        art = ' '.join(article).encode('utf-8')
        f.write(art+'\n')
        
lmtzr = WordNetLemmatizer()
stops = stopwords.words('english')
html = re.compile(r'\<[^\>]*\>')
nonan = re.compile(r'[^a-zA-Z ]')
shortword = re.compile(r'\W*\b\w{1,2}\b')
copyright = 'copyright npr see visit httpwwwnprorg'
 
tag_to_type = {'J': wordnet.ADJ, 'V': wordnet.VERB, 'R': wordnet.ADV}
def get_wordnet_pos(treebank_tag):
    return tag_to_type.get(treebank_tag[:1], wordnet.NOUN)

def clean(text):
    clean_text = nonan.sub('',html.sub('',text))
    words = nltk.word_tokenize(shortword.sub('',clean_text.lower()))
    filtered_words = [w for w in words if not w in stops]
    tags = nltk.pos_tag(filtered_words)
    return ' '.join(
        lmtzr.lemmatize(word, get_wordnet_pos(tag[1]))
        for word, tag in zip(filtered_words, tags)
    )

with open('nprarticles.txt','r') as f:
    with open('corpus.txt','w') as f2:
        text = []
        for line in f:
            text.append(line)
        f2.truncate()
        for line in text:
            text = clean(line)
            f2.write(text.replace(copyright,'') +'\n')
            
def sym_kl(p,q):
    return np.sum([stats.entropy(p,q),stats.entropy(q,p)])
    
dictionary = corpora.Dictionary(line.lower().split() for 
    line in open('corpus.txt','rb'))
once_ids = [tokenid for tokenid, docfreq in 
    dictionary.dfs.iteritems() if docfreq == 1]
dictionary.filter_tokens(once_ids)
dictionary.filter_extremes(no_above=5,keep_n=100000)
dictionary.compactify()

class MyCorpus(object):
    def __iter__(self):
        for line in open('corpus.txt','r'):
            yield dictionary.doc2bow(line.lower().split())

my_corpus = MyCorpus()

l = np.array([sum(cnt for _, cnt in doc) for doc in my_corpus])
def arun(corpus,dictionary,min_topics=1,max_topics,step=1):
    kl = []
    for i in range(min_topics,max_topics,step):
        lda = models.ldamodel.LdaModel(corpus=corpus,
            id2word=dictionary,num_topics=i)
        m1 = lda.expElogbeta
        U,cm1,V = np.linalg.svd(m1)
        #Document-topic matrix
        lda_topics = lda[my_corpus]
        m2 = matutils.corpus2dense(lda_topics, lda.num_topics).transpose()
        cm2 = l.dot(m2)
        cm2 = cm2 + 0.0001
        cm2norm = np.linalg.norm(l)
        cm2 = cm2/cm2norm
        kl.append(sym_kl(cm1,cm2))
    return kl
    
kl = arun(my_corpus,dictionary,max_topics=100)

# Plot kl divergence against number of topics
plt.plot(kl)
plt.ylabel('Symmetric KL Divergence')
plt.xlabel('Number of Topics')
plt.savefig('kldiv.png', bbox_inches='tight')