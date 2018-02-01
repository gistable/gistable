def histogram(filename):
    with open(filename) as fd:
        return Counter(w.strip().lower() for w in fd.read().split() 
               if not (w in nltk.corpus.stopwords.words('english') )).most_common()
print '\n'.join("{}:{}".format(x,y) for x,y in histogram('/Users/fabrizio/Desktop/input.txt'))