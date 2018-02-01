
# coding: utf-8

# In[4]:

from string import punctuation
from sys import argv

def not_with_semicolon(line):
    return not line[0] in punctuation


with open('cmudict-0.7b') as infile:
    lines = filter(not_with_semicolon, infile.read().strip().split('\n'))


# In[6]:

lines = filter(lambda x: not '(' in x, lines)


# In[12]:

cmu_dict = dict()

for l in lines:
    word, phonemes = l.split('  ', 1)
    cmu_dict[word.lower()] = phonemes.split(' ')




# In[29]:

def rhymes(*words):
    try:
        phons_backwards = map(lambda w: cmu_dict[w][::-1], words)
    except KeyError:
        raise Exception('Word not in dictionary.')
    
    matching_phons = list()
    for p_tup in zip(*phons_backwards):
        first_p = p_tup[0]
        if all(p == first_p for p in p_tup[1:]):
            matching_phons.append(first_p)
        else:
            break
            
    return matching_phons and matching_phons[-1][-1] in set(['1', '2'])


# In[30]:

def rhyme_finder(word):
    return filter(lambda w: rhymes(w, word), cmu_dict.keys())


# In[33]:

print '\n'.join(rhyme_finder(argv[-1]))


# In[ ]:



