#-*- coding: utf-8 -*-

"""
GIBBS SAMPLING IMPLEMENTATION FOR LATENT DIRICHLET ALLOCATION (2003)
IMPLEMENTED BY CHANG-UK, PARK
DATA FORMAT: "DocID\t WordID\t FREQUENCY\n"
"""

import sys
import random
import gc
from scipy.special import gamma, gammaln, psi
from scipy.stats import *
from scipy import *
import numpy as np

def OptParams(pathData, candK, nsamples, burnin, interval):
    # DETERMINE OPTIMAL NUMBER OF TOPICS AND CORRESPONDING OTHER PARAMETERS
    # NOTE: THIS TASK MAY TAKE VERY LONG PERIOD OF TIME
    # MODULE USAGE:
    # >>> import myGibbsLDA
    # >>> root = "C:\\Users\\ChangUk\\Desktop\\Research\\data\\"
    # >>> L, K, A, B, Th, Ph = myGibbsLDA.OptParams(root+"data.dat", [5, 10, 20, 50, 100, 200], 300, 150, 2)
    gs = list(range(len(candK)))                                    # LIST FOR CLASS INSTANCES
    bestL = 0
    for i, k in enumerate(candK):                                   # FOR EACH NUMBER OF TOPICS
        trainData.seek(0)
        gs[i] = Sampler(trainData, k)
        tempL = gs[i].kernel(nsamples, burnin, interval)
        if bestL == 0 or bestL < tempL:                             # CHECK IF IT IS BETTER MODEL
            bestL = tempL
            bestAlpha = gs[i].alpha
            bestBeta = gs[i].beta
            bestTheta = gs[i].theta
            bestPhi = gs[i].phi
            bestK = k                                               # CHOOSE THE BEST NUMBER OF TOPICS
        else:
            del(gs[i])
            gc.collect()
    return bestL, bestK, bestAlpha, bestBeta, bestTheta, bestPhi

class Sampler(object):
    # GIBBS SAMPLING FOR LDA INFERENCE
    # MODULE USAGE:
    # >>> import myGibbsLDA
    # >>> root = "C:\\Users\\ChangUk\\Desktop\\Research\\data\\"
    # >>> gs = myGibbsLDA.Sampler(root+"data.dat", 100)
    # >>> l = gs.kernel(500, 300, 2)
    def __init__(self, pathData, ntopics, header = False):
        self.header = header
        self.TOPICS = ntopics                                       # NUMBER OF TOPICS
        self.documents = {}                                         # TRAINING DATA: {DocID: [WordID1, WordID1, WordID2, ...]}
        self.indD = {}                                              # MAP DOCUMENT INTO INDEX: self.indD = {DocID: INDEX}
        self.indV = {}                                              # MAP WORD INTO INDEX: self.indV = {VocabID: INDEX}
        self.DOCS = 0                                               # NUMBER OF DOCUMENTS
        self.VOCABS = 0                                             # NUMBER OF VOCABULARIES
        self.alpha = np.ones(self.TOPICS)
        for i in range(self.TOPICS):
            self.alpha[i] *= 0.01                                   # np.random.gamma(0.1, 1)
        self.beta = 0.01                                            # np.random.gamma(0.1, 1)
        data = open(pathData, "r")
        [self.LoadData(r) for r in data.read().split("\n")]         # LOAD TRAINING DATA INTO 'self.documents'
        for doc in self.documents:
            random.shuffle(self.documents[doc])                     # SHUFFLE WORDS IN EACH DOCUMENT
        data.close()
        self.theta = np.zeros((self.DOCS, self.TOPICS))             # SPACE FOR THETA MATRIX WITH 0s
        self.phi = np.zeros((self.TOPICS, self.VOCABS))             # SPACE FOR PHI MATRIX WITH 0s
        
    def LoadData(self, record):                                     # FOR EACH RECORD
        if len(record) > 0:
            if self.header == True:
                self.header = False
            else:
                r = record.split("\t")                              # r[0] = DocID, r[1] = WordID, r[2] = Frequency
                tmp = [r[1] for i in range(int(r[2]))]
                if not r[0] in self.documents:                      # ADD DOCUMENT
                    self.documents[r[0]] = tmp
                    self.indD[r[0]] = self.DOCS
                    self.DOCS += 1
                else:
                    self.documents[r[0]] += tmp
                if not r[1] in self.indV:                           # ADD WORD
                    self.indV[r[1]] = self.VOCABS
                    self.VOCABS += 1

    def assignTopics(self, doc, word, pos):                         # DROW TOPIC SAMPLE FROM FULL-CONDITIONAL DISTRIBUTION
        d = self.indD[doc]
        w = self.indV[word]
        z = self.topicAssignments[d][pos]                           # TOPIC ASSIGNMENT OF WORDS FOR EACH DOCUMENT
        self.cntTW[z, w] -= 1
        self.cntDT[d, z] -= 1
        self.cntT[z] -= 1
        self.lenD[d] -= 1
        
        # FULL-CONDITIONAL DISTRIBUTION
        prL = (self.cntDT[d] + self.alpha) / (self.lenD[d] + np.sum(self.alpha))
        prR = (self.cntTW[:,w] + self.beta) / (self.cntT + self.beta * self.VOCABS)
        prFullCond = prL * prR                                      # FULL-CONDITIONAL DISTRIBUTION
        prFullCond /= np.sum(prFullCond)                            # TO OBTAIN PROBABILITY
        # NOTE: 'prFullCond' is MULTINOMIAL DISTRIBUTION WITH THE LENGTH, NUMBER OF TOPICS, NOT A VALUE
        new_z = np.random.multinomial(1, prFullCond).argmax()       # RANDOM SAMPLING FROM FULL-CONDITIONAL DISTRIBUTION
        self.topicAssignments[d][pos] = new_z
        self.cntTW[new_z, w] += 1
        self.cntDT[d, new_z] += 1
        self.cntT[new_z] += 1
        self.lenD[d] += 1

    def LogLikelihood(self):                                        # FIND (JOINT) LOG-LIKELIHOOD VALUE
        l = 0
        for z in range(self.TOPICS):                                # log p(w|z,\beta)
            l += gammaln(self.VOCABS * self.beta)
            l -= self.VOCABS * gammaln(self.beta)
            l += np.sum(gammaln(self.cntTW[z] + self.beta))
            l -= gammaln(np.sum(self.cntTW[z] + self.beta))
        for doc in self.documents:                                  # log p(z|\alpha)
            d = self.indD[doc]
            l += gammaln(np.sum(self.alpha))
            l -= np.sum(gammaln(self.alpha))
            l += np.sum(gammaln(self.cntDT[d] + self.alpha))
            l -= gammaln(np.sum(self.cntDT[d] + self.alpha))
        return l

    def findAlphaBeta(self):
        # ADJUST ALPHA AND BETA BY USING MINKA'S FIXED-POINT ITERATION
        numerator = 0
        denominator = 0
        for d in range(self.DOCS):
            numerator += psi(self.cntDT[d] + self.alpha) - psi(self.alpha)
            denominator += psi(np.sum(self.cntDT[d] + self.alpha)) - psi(np.sum(self.alpha))
        self.alpha *= numerator / denominator                       # UPDATE ALPHA
        numerator = 0
        denominator = 0
        for z in range(self.TOPICS):
            numerator += np.sum(psi(self.cntTW[z] + self.beta) - psi(self.beta))
            denominator += psi(np.sum(self.cntTW[z] + self.beta)) - psi(self.VOCABS * self.beta)
        self.beta = (self.beta * numerator) / (self.VOCABS * denominator)       # UPDATE BETA

    def findThetaPhi(self):
        th = np.zeros((self.DOCS, self.TOPICS))                     # SPACE FOR THETA
        ph = np.zeros((self.TOPICS, self.VOCABS))                   # SPACE FOR PHI
        for d in range(self.DOCS):
            for z in range(self.TOPICS):
                th[d][z] = (self.cntDT[d][z] + self.alpha[z]) / (self.lenD[d] + np.sum(self.alpha))
        for z in range(self.TOPICS):
            for w in range(self.VOCABS):
                ph[z][w] = (self.cntTW[z][w] + self.beta) / (self.cntT[z] + self.beta * self.VOCABS)
        return ph, th

    def kernel(self, nsamples, burnin, interval):                   # GIBBS SAMPLER KERNEL
        if(nsamples <= burnin):                                     # BURNIN CHECK
            print("ERROR: BURN-IN POINT EXCEEDS THE NUMBER OF SAMPLES")
            sys.exit(0)
        print("# of DOCS:", self.DOCS)                              # PRINT TRAINING DATA INFORMATION
        print("# of TOPICS:", self.TOPICS)
        print("# of VOCABS:", self.VOCABS)
        
        # MAKE SPACE FOR TOPIC-ASSIGNMENT MATRICES WITH 0s
        self.topicAssignments = {}                                  # {INDEX OF DOC: [TOPIC ASSIGNMENT]}
        for doc in self.documents:
            d = self.indD[doc]
            self.topicAssignments[d] = [0 for word in self.documents[doc]]
        self.cntTW = np.zeros((self.TOPICS, self.VOCABS))           # NUMBER OF TOPICS ASSIGNED TO A WORD
        self.cntDT = np.zeros((self.DOCS, self.TOPICS))             # NUMBER OF TOPICS ASSIGNED IN A DOCUMENT
        self.cntT = np.zeros(self.TOPICS)                           # ASSIGNMENT COUNT FOR EACH TOPIC
        self.lenD = np.zeros(self.DOCS)                             # ASSIGNMENT COUNT FOR EACH DOCUMENT = LENGTH OF DOCUMENT
        
        # RANDOMLY ASSIGN TOPIC TO EACH WORD
        for doc in self.documents:
            for i, word in enumerate(self.documents[doc]):
                d = self.indD[doc]
                w = self.indV[word]
                rt = random.randint(0, self.TOPICS-1)               # RANDOM TOPIC ASSIGNMENT
                self.topicAssignments[d][i] = rt                    # RANDOMLY ASSIGN TOPIC TO EACH WORD
                self.cntTW[rt, w] += 1
                self.cntDT[d, rt] += 1
                self.cntT[rt] += 1
                self.lenD[d] += 1
                
        # COLLAPSED GIBBS SAMPLING
        print("INITIAL STATE")
        print("|- Likelihood:", self.LogLikelihood())               # FIND (JOINT) LOG-LIKELIHOOD
        print("|- Alpha:", end="")
        for i in range(self.TOPICS):
            print(" %.5f" % self.alpha[i], end="")
        print("\n|- Beta: %.5f" % self.beta)
        SAMPLES = 0
        for s in range(nsamples):
            for doc in self.documents:
                for i, word in enumerate(self.documents[doc]):
                    self.assignTopics(doc, word, i)                 # DROW TOPIC SAMPLE FROM FULL-CONDITIONAL DISTRIBUTION
            self.findAlphaBeta()                                    # UPDATE ALPHA AND BETA VALUES
            lik = self.LogLikelihood()
            print("SAMPLE #" + str(s))
            print("|- Likelihood:", lik)
            print("|- Alpha:", end="")
            for i in range(self.TOPICS):
                print(" %.5f" % self.alpha[i], end="")
            print("\n|- Beta: %.5f" % self.beta)
            if s > burnin and s % interval == 0:                    # FIND PHI AND THETA AFTER BURN-IN POINT
                ph, th = self.findThetaPhi()
                self.theta += th
                self.phi += ph
                SAMPLES += 1
        self.theta /= SAMPLES                                       # AVERAGING GIBBS SAMPLES OF THETA
        self.phi /= SAMPLES                                         # AVERAGING GIBBS SAMPLES OF PHI
        return lik

if __name__ == "__main__":
    print("GIBBS SAMPLING FOR LDA INFERENCE.")