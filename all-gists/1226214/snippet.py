documents = [ dict(
            email=open("conference/%d.txt" % n).read().strip(), 
            category='conference') for n in range(1,372) ]
documents.extend([ dict( 
            email=open("job/%d.txt" % n).read().strip(),
            category='job') for n in range(1,275)])
documents.extend([ dict( 
            email=open("spam/%d.txt" % n).read().strip(), 
            category='spam') for n in range(1,799) ])


from email import message_from_string
from BeautifulSoup import BeautifulSoup as BS
from re import split
for n in range(len(documents)):
  html = message_from_string(documents[n]['email']).get_payload()
  while not isinstance(html, str):                 # Multipart problem
    html = html[0].get_payload()
  text = ' '.join(BS(html).findAll(text=True))      # Strip HTML
  documents[n]['html'] = html
  documents[n]['text'] = text
  documents[n]['words'] = split('\W+', text)        # Find words


import nltk
all_words = nltk.FreqDist(w.lower() for d in documents for w in d['words'])
word_features = all_words.keys()[:2000]


def document_features(document):
  document_words = set(document['words'])
  features = {}
  for word in word_features:
    features['contains(%s)' % word] = (word in document_words)
  return features


import random
random.shuffle(documents)

featuresets = [(document_features(d), d['category']) for d in documents]
train_set, test_set = featuresets[721:], featuresets[:721]

classifier = nltk.NaiveBayesClassifier.train(train_set)


