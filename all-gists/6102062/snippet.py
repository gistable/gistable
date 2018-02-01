import requests
from collections import deque
class SolrTermVectorCollector(object):
    def __pathToTvrh(self, solrUrl, collection):
        import urlparse
        userSpecifiedUrl = urlparse.urlsplit(solrUrl)
        schemeAndNetloc = urlparse.SplitResult(scheme=userSpecifiedUrl.scheme,
                                               netloc=userSpecifiedUrl.netloc,
                                               path='',
                                               query='',
                                               fragment='')
        solrBaseUrl = urlparse.urlunsplit(schemeAndNetloc)
        solrBaseUrl = urlparse.urljoin(solrBaseUrl, 'solr/')
        solrBaseUrl = urlparse.urljoin(solrBaseUrl, collection + '/')
        solrBaseUrl = urlparse.urljoin(solrBaseUrl, 'tvrh')
        return solrBaseUrl
    
    def __init__(self, solrUrl="http://localhost:8983/solr",
            collection="collection1",
            field='Title',
            feature='tf-idf',
            batchSize=10000,
            numDocs=100000):
        self.solrTvrhUrl = self.__pathToTvrh(solrUrl, collection)
        self.field = field
        self.feature = feature
        self.batchSize = batchSize
        self.numDocs = numDocs
        self.sess = requests.Session()
        self.count = 0

        self.termVectors = []

    def __iter__(self):
        return self

    def next(self):
        if self.count >= self.numDocs:
            raise StopIteration
        if len(self.termVectors) == 0:
            #then get some more!
            params = {"tv.fl": self.field,
                      "fl": "nonexistentfield",#to limit the volumn of data returned
                      "wt": "json",
                      "tv.all": "true",
                      "rows": min(self.batchSize, self.numDocs-self.count),
                      "start": self.count,
                      "q": self.field + ":*"}
            resp = self.sess.get(url=self.solrTvrhUrl, params=params)
            if resp.status_code != 200:
                raise IOError("HTTP Status " + str(resp.status_code))
            self.termVectors = deque(resp.json()['termVectors'][3::2])#overcoming weird non-dictionary json format

        if len(self.termVectors) == 0:
            #then Solr's our of documents
            raise StopIteration
        tv = self.termVectors.popleft()
        id = tv[1]
        termVector = {}
        data = tv[3] #all of the terms and features in this vector
        for i in xrange(0,len(data),2):
            term = data[i]
            featureValue = [data[i+1][j+1] for j in range(len(data[i+1])) if data[i+1][j] == self.feature][0]
            termVector[term] = featureValue
        self.count += 1
        return (id, termVector)



from collections import defaultdict
class StringIndexDict(object):
    def __init__(self):
        self.currentIndex = -1
        self.stringDict = defaultdict(self.count)
        self.indexDict = {}

    def count(self):
        self.currentIndex += 1
        self.indexDict[self.currentIndex] = self.keyInQuestion #kinda funky, but since this will always be single threaded, it's ok
        return self.currentIndex

    def __getitem__(self,key):
        self.keyInQuestion = key
        if isinstance(key,basestring):
            return self.stringDict[key]
        else :
            return self.indexDict[key]

    def size(self):
        return self.currentIndex + 1

    def freeze(self):
        #allow no more changes
        self.stringDict.default_factory = None



import scipy.sparse
import numpy
import sparsesvd
class TermDocCollection(object):
    def __init__(self,source=None,numTopics=10):
        self._docDict = StringIndexDict()
        self._termDict = StringIndexDict()
        self._termVectors = []
        self.numTopics = numTopics
        for termVector in source:
            self._termVectors.append(
                (
                    self._docDict[termVector[0]],
                    {self._termDict[k]:v for k,v in termVector[1].iteritems()}
                )
            )
        self._termDict.freeze()
        self._docDict.freeze()

        #memoized later:
        self._svd = None
        self._cscMatrix = None
        self._uPrime = None


    def _getCscMatrix(self):
        if self._cscMatrix is not None:
            return self._cscMatrix
        num_nnz, data, indices, indptr = 0, [], [], [0]
        for termVector in self._termVectors:
            newIndices = [i for i in termVector[1].keys()]
            newValues = [v for v in termVector[1].values()]
            indices.extend(newIndices)
            data.extend(newValues)
            num_nnz += len(newValues)
            indptr.append(num_nnz)
        numTerms = self._termDict.size()
        numDocs = self._docDict.size()
        data = numpy.asarray(data)
        indices = numpy.asarray(indices)
        self._cscMatrix = scipy.sparse.csc_matrix((data, indices, indptr), shape=(numTerms, numDocs))
        return self._cscMatrix

    def _getSvd(self):
        if self._svd is not None:
            return self._svd
        self._svd = sparsesvd.sparsesvd(self._getCscMatrix(), self.numTopics)
        return self._svd

    def _getUprime(self):
        if self._uPrime is not None:
            return self._uPrime
        u,s,v = self._getSvd()
        self._uPrime = numpy.dot(u.T,numpy.diag(s))
        return self._uPrime

    def getBlurredTerms(self,doc,cutoff):
        if isinstance(doc,str):
            doc = self._docDict[doc]
        uPrime = self._getUprime()
        _,_,v = self._getSvd()
        blurredField = numpy.dot(uPrime,v[:,doc])
        tokenIds = numpy.where(blurredField>cutoff)[0]
        tokens = [self._termDict[id] for id in tokenIds]
        return tokens



def main(field,collection,solrUrl):
    stvc = SolrTermVectorCollector(field='Body',feature='tf',batchSize=1000)
    tdc = TermDocCollection(source=stvc,numTopics=100)
    print tdc.getBlurredTerms('20710',0.2)
    print tdc.getBlurredTerms('17250',0.1)
    print tdc.getBlurredTerms('11113',0.1)

if __name__ == "__main__":
    from sys import argv
    if len(argv)==0:
        raise Exception("usage: python SemanticAnalyzer.py fieldname [collection [solrUrl]]")

    field = argv[1]
    collection = argv[2] if len(argv)>2 else "collection1"
    solrUrl = argv[3] if len(argv)>3 else "http://localhost:8983/solr"
    main(field,collection,solrUrl)
