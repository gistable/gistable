""" A script to attempt the compression of written english 
to the chinese character set """

import os
from collections import OrderedDict
from math import log
import itertools
from collections import Counter


#grap a corpus from a text file
corpus = open( os.path.join('corpus','fullcorpus.txt') , 'r' ).read()

#Find the words in the corpus, and count them
words = corpus.split()
realwords = [w for w in words if len(w) > 1]
wordcount = Counter(realwords)
tot = sum(wordcount.values())


#Number of characters to work with 20931
def chinesechars():
    """ Define the chinese character iterator """
    chinesestart = 0x4E00
    chinesefinish = 0x9FA5 + 30
    numchars = chinesefinish - chinesestart
    
    for i in xrange(numchars):
        yield unichr(chinesestart + i )
        
characters = chinesechars()


# Define our translation dictionary
rep = OrderedDict()

# take the 1500 most common words
for word,count in wordcount.most_common(1500):
    rep[word + ' '] = next(characters)

#replace these symbols in the corpus
newcorpus = corpus[:]
for f,t in rep.iteritems():
    newcorpus = newcorpus.replace(f,t)
    

#Compute the entropy of a string
def entropy(sample):
    """ Compute the entropy of the text,
        shooting for 14.35 """
    charcount = Counter(sample)
    tot = float(sum(charcount.values()))
    
    shans = sum(-x/tot * log( x/tot, 2) for x in charcount.values() )
    return shans
        
    

     
def translate(st):
    """ Translate some strange sequence back to the original """
    for f in reversed(rep):
        t = rep[f]
        st = st.replace(t,f)
    return st
    



def display(guys):
    """ Display the results of a step """
    for w,c in guys:
        print ' <' + translate(w) + '>: {num} | '.format(num=c),
    print


    print
    print
    chars = Counter(newcorpus)
    bigums = chars.most_common(20)

    for w,c in guys:
        print ' [' + translate(w) + ']: {num} | '.format(num=c),

    print
    print
    print

def compute_seqs():
    """ Compute the most common pairs and words in the source """
    words = newcorpus.split()
    words = [w + ' ' for w in words if len(w) > 1]
    
    wordcounter = Counter(words)
    wordcounter = wordcounter+wordcounter
    
    #Generate pairs by tee-ing the iterator
    one,two = itertools.tee(iter(newcorpus))
    next(two)
    
    pairs = itertools.izip(one,two)
    pairs = ( a+b for a,b in pairs )
    paircounter = Counter(pairs)

    
    totcounter = paircounter + wordcounter
    
    z = totcounter.most_common(100)

    return totcounter
    
    
def addguys(guys):
    """ Add some guys to the global translation dictionary """
    global rep
    for w,c in guys:
        try:
            rep[w] = next(characters)
        except StopIteration:
            print "All Done!"
            break
    
def text_replace():
    """ Translate the corpus """
    global newcorpus
    for f,t in rep.iteritems():
        newcorpus = newcorpus.replace(f,t)


def encode(text):
    """ Encode a string with the dictionary """
    for f,t in rep.iteritems():
        text = text.replace(f,t)
    return text

def timestep():
    """ Do a timestep.  Find the most common pairs,
        display the results
        add the new pair to the dictionary
        update the corpus
    """
    z = compute_seqs().most_common(100)
    
    display(z)
    
    addguys(z)
    
    text_replace()
    

if __name__ == '__main__':
    #do 194 iterations
    for i in xrange(194):
        timestep()
        print
        print i
        print
    