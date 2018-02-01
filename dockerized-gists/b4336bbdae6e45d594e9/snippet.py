from nltk import pos_tag
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer, WordNetLemmatizer

stemmer = PorterStemmer()
lemmatiser = WordNetLemmatizer()

print("Stem %s: %s" % ("going", stemmer.stem("going")))
print("Stem %s: %s" % ("gone", stemmer.stem("gone")))
print("Stem %s: %s" % ("goes", stemmer.stem("goes")))
print("Stem %s: %s" % ("went", stemmer.stem("went")))
"""
Stem going: go
Stem gone: gone
Stem goes: goe
Stem went: went
"""

print("Without context")
print("Lemmatise %s: %s" % ("going", lemmatiser.lemmatize("going")))
print("Lemmatise %s: %s" % ("gone", lemmatiser.lemmatize("gone")))
print("Lemmatise %s: %s" % ("goes", lemmatiser.lemmatize("goes")))
print("Lemmatise %s: %s" % ("went", lemmatiser.lemmatize("went")))
"""
Without context
Lemmatise going: going
Lemmatise gone: gone
Lemmatise goes: go
Lemmatise went: went
"""

print("With context")
print("Lemmatise %s: %s" % ("going", lemmatiser.lemmatize("going", pos="v")))
print("Lemmatise %s: %s" % ("gone", lemmatiser.lemmatize("gone", pos="v")))
print("Lemmatise %s: %s" % ("goes", lemmatiser.lemmatize("goes", pos="v")))
print("Lemmatise %s: %s" % ("went", lemmatiser.lemmatize("went", pos="v")))
"""
With context
Lemmatise going: go
Lemmatise gone: go
Lemmatise goes: go
Lemmatise went: go
"""

print("Stem %s: %s" % ("studying", stemmer.stem("studying")))
print("Stem %s: %s" % ("study", stemmer.stem("study")))
print("Stem %s: %s" % ("studies", stemmer.stem("studies")))
print("Stem %s: %s" % ("studied", stemmer.stem("studied")))
"""
Stem studying: studi
Stem study: studi
Stem studies: studi
Stem studied: studi
"""

print("Without context")
print("Lemmatise %s: %s" % ("studying", lemmatiser.lemmatize("studying")))
print("Lemmatise %s: %s" % ("study", lemmatiser.lemmatize("study")))
print("Lemmatise %s: %s" % ("studies", lemmatiser.lemmatize("studies")))
print("Lemmatise %s: %s" % ("studied", lemmatiser.lemmatize("studied")))
"""
Without context
Lemmatise studying: studying
Lemmatise study: study
Lemmatise studies: study
Lemmatise studied: studied
"""

print("With context")
print("Lemmatise %s: %s" % ("studying", lemmatiser.lemmatize("studying", pos="v")))
print("Lemmatise %s: %s" % ("study", lemmatiser.lemmatize("study", pos="v")))
print("Lemmatise %s: %s" % ("studies", lemmatiser.lemmatize("studies", pos="v")))
print("Lemmatise %s: %s" % ("studied", lemmatiser.lemmatize("studied", pos="v")))
"""
With context
Lemmatise studying: study
Lemmatise study: study
Lemmatise studies: study
Lemmatise studied: study
"""

s = "This is a simple sentence"
tokens = word_tokenize(s)
tokens_pos = pos_tag(tokens)

print(tokens_pos)
"""
[('This', 'DT'), ('is', 'VBZ'), ('a', 'DT'), ('simple', 'JJ'), ('sentence', 'NN')]
"""