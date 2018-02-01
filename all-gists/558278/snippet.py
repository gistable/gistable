import numpy as np

def symdirichlet(alpha, n):
    v = np.zeros(n)+alpha
    return np.random.dirichlet(v)


def exp_digamma(x):
    if x < 0.1:
        return x/100
    a = x*x
    b = a*x
    c = b*x
    return x - 0.5 + 1./(24*x) 

exp_digamma = np.vectorize(exp_digamma)


import re
wre = re.compile(r"(\w)+")
def get_words(text, stop=True):
    "A simple tokenizer"
    l = 0
    while l < len(text):
        s = wre.search(text,l)
        try:
            w = text[s.start():s.end()].lower()
            if stop:
                yield w
            elif w not in stoplist:
                yield w
            l = s.end()
        except:
            break


class EmLda(object):
    def __init__(self, docs, nt):
        self.Nt = nt
        self.docs = []
        self.all_words = []
        self.reverse_map = {}
        self.Nd = 0
        for d in docs:
            doc = []
            self.docs.append(doc)
            self.Nd += 1
            for w in get_words(d):
                if len(w) < 5: continue
                if not w in self.reverse_map:
                    self.reverse_map[w] = len(self.all_words)
                    self.all_words.append(w)
                doc.append(self.reverse_map[w])
        self.V = len(self.all_words)
        self.ctopics = np.zeros((self.Nt, self.V))
        self.doccounts = np.zeros((self.Nd, self.Nt))
        self.ptopics = np.zeros((self.Nt, self.V))
        self.docprobs = np.zeros((self.Nd, self.Nt))
        self.beta = 1.
        self.alpha = 1.
        for d in xrange(self.Nd):
            for i,w in enumerate(self.docs[d]):
                zw = symdirichlet(self.beta, self.Nt)
                self.ctopics.T[w] += zw
                self.doccounts[d] += zw
        self.m()
       


    def e(self):
        self.ctopics.fill(0)
        self.doccounts.fill(0)
        for d in xrange(self.Nd):
            for i,w in enumerate(self.docs[d]):
                zw = self.ptopics.T[w].copy()
                zw *= self.docprobs[d]
                zw /= np.sum(zw)
                self.ctopics.T[w] += zw
                self.doccounts[d] += zw

    def m(self):
        self.ptopics.fill(0)
        self.docprobs.fill(0)
        self.ptopics += self.ctopics + self.alpha
        self.ptopics /= np.sum(self.ctopics, axis=1).reshape((-1,1))
        self.docprobs += self.doccounts + self.beta
        self.docprobs /= np.sum(self.docprobs, axis=1).reshape((-1,1))

    def iterate(self):
        self.e()
        self.m()
        

    def run(self, n):
        for i in xrange(n):
            print "iter", i
            import sys
            sys.stdout.flush()
            self.iterate()
        for w in xrange(100):
            print "word", self.all_words[w], 
            print "topics", self.ptopics.T[w]/np.sum(self.ptopics.T[w])
        for i in xrange(self.Nt):
            print
            print
            print "Topic", i
            print
            print_topic(self, self.ptopics[i], 40)


class PrLda(EmLda):

    def __init__(self, *args):
        super(PrLda, self).__init__(*args)
        self.Nw = sum(len(d) for d in self.docs)
        c = 0
        self.sigma = 15.

    def e(self):
        self.do_lambda()
        self.do_z()
    
    def do_lambda(self):
        self.ptheta = [[] for i in xrange(self.V)]
        self.ctopics.fill(0)
        self.doccounts.fill(0)
        for d in xrange(self.Nd):
            for i,w in enumerate(self.docs[d]):
                zw = self.ptopics.T[w].copy()
                zw *= self.docprobs[d]
                zw /= np.sum(zw)
                self.ptheta[w].append(zw)
        self.lbda = []
        self.ptheta = map(np.array, self.ptheta)
        for w in xrange(self.V):
            self.lbda.append(self.optimize_lambda(self.ptheta[w]))

    def optimize_lambda(self, ptheta, steps=50, lrate=1.):
        lbda = np.ones(ptheta.shape[1])
        lbda /= np.sum(lbda).T
        lbda *= self.sigma
        prevobj = np.inf
        n = 0
        while True:
            obj = np.sum(np.sum(ptheta,axis=0).T*np.exp(-lbda))
            if  n > 5 and  prevobj - obj < 0.01*obj:
                break
            n += 1
            prevobj = obj
            # do the gradient descent
            lbda += lrate*np.sum(ptheta,axis=0)*np.exp(-lbda)
            # truncate
            lbda *= lbda>0
            # project it into the l1 ball with diameter sigma
            ll = -np.sort(-lbda)
            cs = np.argmin(((ll-self.sigma).cumsum()/(np.arange(len(ll))+1.))) >= 0
            theta = ll[cs-1]
            lbda -= theta
            lbda *= lbda > 0                
        return lbda

    def do_z(self):
        indices = [0 for i in xrange(self.V)]
        for d in xrange(self.Nd):
            for i,w in enumerate(self.docs[d]):
                zw = self.ptheta[w][indices[w]]
                zw *= np.exp(-self.lbda[w])
                zw /= np.sum(zw)
                indices[w] += 1
                self.ctopics.T[w] += zw
                self.doccounts[d] += zw


class VarLda(EmLda):
    def e(self):
        self.ctopics.fill(0)
        self.doccounts.fill(0)
        for d in xrange(self.Nd):
            for i,w in enumerate(self.docs[d]):
                zw = self.ptopics.T[w].copy()
                zw *= self.docprobs[d]
                zw = exp_digamma(zw)/exp_digamma(np.sum(zw))
                self.ctopics.T[w] += zw
                self.doccounts[d] += zw



def print_topic(model, t, n):
    s = np.argsort(-t)
    for w in s[:n]:
        print "     ",model.all_words[w]


if __name__ == '__main__':
    import sys
    docs = []
    nt = int(sys.argv[1])
    import os
    for fname in os.listdir(sys.argv[2]):
        if not fname.startswith("."):
            docs.append(file(os.path.join(sys.argv[2],fname)).read())
    el = VarLda(docs, nt)
    el.run(10)
    el = EmLda(docs, nt)
    el.run(10)
    el = PrLda(docs, nt)
    el.run(10)
    el = PrLda(docs, nt)
    el.sigma = 150
    el.run(10)
