import numpy as np
from gensim import matutils
def normalize(v):
  '''normalize' a vector, in the traditional linear algebra sense.'''
  norm=np.linalg.norm(v)
  if norm==0:
    return v
  return v/norm

def reject(A,B):
  '''Create a 'projection', and subract it from the original vector'''
  project = np.linalg.linalg.dot(A, normalize(B)) * normalize(B)
  return A - project

def reject_word(A, B):
  '''returns most_similar for word A, while rejecting words with meanings closer to B.
  Seems to work better than just giving in negative words.
  '''
  r = reject(model[A], model[B])
  dists = np.linalg.linalg.dot(model.syn0, r)
  best  = matutils.argsort(dists, topn = 500, reverse = True)
  result = [(model.index2word[sim], float(dists[sim])) for sim in best]
  return result