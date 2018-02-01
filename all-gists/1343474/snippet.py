from multiprocessing import Pool
import string
import random

def mapFunction(letter):
  return (letter, 1)

def partition(tuples):
  mapping = {}
  for t in tuples:
    try:
      mapping[t[0]].append (t)
    except KeyError:
      mapping[t[0]] = [t]
  return mapping
  
def reduceFunction(mapping):  
  return (mapping[0], sum(pair[1] for pair in mapping[1]))
  
if __name__ == '__main__':    
  pool = Pool(processes=10)  

  letters = [random.choice(string.uppercase) for i in range(30)]
  print "letters: ", letters, "\n"
  tuples = pool.map(mapFunction, letters)
  print "tuples: ", tuples, "\n"
  mapping = partition(tuples)
  print "mapping: ", mapping, "\n"
  results = pool.map(reduceFunction, mapping.items())    
  results.sort(key=lambda r: r[1])
  results.reverse()
  for r in results:
    print "The letter %s appeared %d times" % r