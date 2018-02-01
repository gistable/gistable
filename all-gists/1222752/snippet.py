#!/usr/bin/python -O
import numpy as np
from numpy import array

A, C, G, T = 0, 1, 2, 3
int_to_char = {0:'A', 1:'C', 2:'G', 3:'T'}

#indel = -1
#scoring = array([[1,-1,-1,-1],
                 #[-1,1,-1,-1],
                 #[-1,-1,1,-1],
                 #[-1,-1,-1,1]])
indel = -5 
scoring = array([[2,-4,-1,-4],
                 [-4,2,-4,-1],
                 [-1,-4,2,-4],
                 [-4,-1,-4,2]])

class AlignmentFinder(object):
    def __init__(self, seq1, seq2):
        self.seq1 = seq1
        self.seq2 = seq2
        self.D = None

    def find_gobal_alignment(self):
        self.D = np.zeros((self.seq1.size+1, self.seq2.size+1), dtype=np.int16)
        self._compute_array()
        print self.D
        return self._traceback()

    def _compute_array(self):
        for i in xrange(self.seq1.size+1):
            self.D[i,0] = i*indel
        for j in xrange(self.seq2.size+1):
            self.D[0,j] = j*indel
        for i in xrange(1, self.seq1.size+1):
            for j in xrange(1, self.seq2.size+1):
                self.D[i,j] = max(  self.D[i-1, j-1] + self._get_score(i, j),
                                    self.D[i-1, j] + indel,
                                    self.D[i, j-1] + indel)
    def _get_score(self, i, j):
        ''' The indexing is quite tricky because the matrix as one more row & column.
        That causes a shift between the matrix index and the sequence indices.
        Therefore, to obtain the correct nucleotide in the sequence, we must
        substract 1 to the matrix index. '''
        return scoring[self.seq1[i-1], self.seq2[j-1]]
    
    def _get_aligned_pair(self, i, j):
        n1 = int_to_char[self.seq1[i-1]] if i>0 else '_'
        n2 = int_to_char[self.seq2[j-1]] if j>0 else '_'
        return (n1, n2)

    def _traceback(self):
        alignment= []
        i = self.seq1.size
        j = self.seq2.size
        while i >0 and j>0:
            if self.D[i-1, j-1] + self._get_score(i, j) == self.D[i,j]:
                alignment.append(self._get_aligned_pair(i, j))
                i -= 1
                j -= 1
            elif self.D[i-1, j] + indel == self.D[i,j]:
                alignment.append(self._get_aligned_pair(i, 0))
                i -= 1
            else:
                alignment.append(self._get_aligned_pair(0, j))
                j -= 1
        while i > 0:
            alignment.append(self._get_aligned_pair(i, 0))
            i -= 1
        while j > 0:
            alignment.append(self._get_aligned_pair(0, j))
            j -= 1
        alignment.reverse()
        return alignment  

def print_sequences(pairs):
    top_seq = []
    bottom_seq = []
    for (b, t) in pairs:
        bottom_seq.append(b)
        top_seq.append(t)
    for n in top_seq:
        print n,
    print ' '
    for n in bottom_seq:
        print n,

if __name__ == "__main__":
    s1 = array([G, T, A, C, A, G, T, A], dtype=np.int16)
    s2 = array([G, G, T, A, C, G, T], dtype=np.int16)
    aligner = AlignmentFinder(s1, s2)
    pairs = aligner.find_gobal_alignment()
    print_sequences(pairs)
