# more info: http://webmining.olariu.org/ubervu-hackaton-relationship-tagcloud

from nltk import pos_tag, word_tokenize
import en # Nodebox English Linguistics library
import urllib, urllib2, re
import json
from time import time

def fetch_url(url, get=None, post=None):
   user_agent = 'Andrei Olariu\'s Web Mining for Dummies'
   headers = {'User-Agent': user_agent}
   if get:
       data = urllib.urlencode(get)
       url = "%s?%s" % (url, data)
   print url
   req = urllib2.Request(url, post, headers)
   try:
       response = urllib2.urlopen(req).read()
       response = json.loads(response)
   except Exception, e:
       print 'error in reading %s: %s' % (url, e)
       return None
   return response

def get_tweets(values):
 '''
   do a series of api calls at ubervu's api to get all
   tweets matching the filtering options
 '''
 url = 'http://api.contextvoice.com/1.2/mentions/search/'
 data = []
 val = time()
 while True:
   response = fetch_url(url, values)
   if not response or response['total'] == 0:
       break
   data.extend(response['results'])
   val = min([t['published'] for t in response['results']])
   values.update({
       'until': val - 1,
   })
 return data

def tag_and_filter(text):
  ''' Takes a text, breaks the words apart, gets the POS tag for
    each one of them, keeps only the nouns, verbs and adjectives
    and puts them in the singular/present form
  '''
  words = word_tokenize(text.lower())
  filtered_words = []
  i = 0
  while i < len(words):
    # filter RT, twitter names, hashtags, links
    if words[i] in ('rt', '', '%'):
      i += 1
    elif words[i] in ('@', '#'):
      i += 2
    elif words[i] == 'http':
      i += 3
    else:
      word = re.findall(r'\w+', words[i])
      if word:
        filtered_words.append(word[0])
      i += 1

  # Beware, nltk is pretty good at POS-ing, but very slow
  # For better speed (but lower precision) use nodebox ling
  pos_tags = pos_tag(filtered_words)
  filtered = []
  accepted = ['JJ', 'JJR', 'JJS', 'NN', 'NNP', 'NNPS', 'NNS', 'PRP', 'RB', \
      'RBR', 'RBS', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
  # this is even better than stemming
  for word, pos in pos_tags:
    if pos in accepted:
      if pos.startswith('NN'):
        word = en.noun.singular(word)
      elif pos.startswith('VB'):
        word = en.verb.infinitive(word)
      filtered.append((word, pos))
  return filtered
  
def is_match(exp, text):
   found = None
   found = re.search(exp, text)
   return found != None

def nouns_and_verbs(sentences):
   '''
     Gets data like sentence = [('Jill', 'NNP'), ('Jack', 'NNP'), 
	 ('like', 'VB'), ('apples', 'NN'), ('oranges', 'NN')]
     Returns data like ([('Jill', 'like'), ('Jack', 'like')],
     [('like', 'apples'), ('like', 'oranges')])
   '''
   def is_noun(word):
       return is_match('NN(PS?|S)?', word)
   def is_verb(word):
       return is_match('VB(D|G|N|P|Z)?', word)
   nv = []
   vn = []
   for s in sentences:
       nouns_1 = []
       verbs = []
       nouns_2 = []
       found_verb = False
       for w in s:
           if is_verb(w[1]):
               found_verb = True
               verbs.append(w[0])
           elif is_noun(w[1]):
               if found_verb == False:
                   nouns_1.append(w[0])
               else:
                   nouns_2.append(w[0])
           else:
               print w, ' not verb or noun'
       for n in nouns_1:
           for v in verbs:
               nv.append((n, v))
       for v in verbs:
           for n in nouns_2:
               vn.append((v, n))
   return (nv, vn)
   
def update_model(model, sv_texts, vs_texts):
  '''
    Receives a list of nouns_and_verbs and one of verbs_and_nouns
    Updates a model
  '''
  # 'who' stands for nouns, 'what' for verbs
  # given a pair (a, b), an 'out' link will be created from a to b
  # and an 'in' link from b to a (in case we want fast querying)
  for pair in sv_texts:
    who, what = pair
    if not who or not what:
      continue
    if who not in model['who']:
      model['who'][who] = {'in': {}, 'out': {}}
    if what not in model['who'][who]['out']:
      model['who'][who]['out'][what] = 0
    model['who'][who]['out'][what] += 1
    
    if what not in model['what']:
      model['what'][what] = {'in': {}, 'out': {}}
    if who not in model['what'][what]['in']:
      model['what'][what]['in'][who] = 0
    model['what'][what]['in'][who] += 1
    
  for pair in vs_texts:
    what, who = pair
    if not who or not what:
      continue    
    if who not in model['who']:
      model['who'][who] = {'in': {}, 'out': {}}
    if what not in model['who'][who]['in']:
      model['who'][who]['in'][what] = 0
    model['who'][who]['in'][what] += 1
    
    if what not in model['what']:
      model['what'][what] = {'in': {}, 'out': {}}
    if who not in model['what'][what]['out']:
      model['what'][what]['out'][who] = 0
    model['what'][what]['out'][who] += 1

def get_links(model, word, word_type=None):
    '''
      Queries the model for a word
	  The word_type (who/what) should be given, because some words
	  may appear in both categories
	'''
    if not word_type:
        if word in model['who']:
            word_type = 'who'
        if word in model['what']:
            if word_type:
                print 'word may be a verb or a noun, please specify'
                return None
            word_type = 'what'
    if not word_type:
        return None
    threshold = 0.08
    in_list = model[word_type][word]['in'].items()
    in_list.sort(key=lambda x: -x[1])
    total = sum([x[1] for x in in_list])
    filtered = []
    for element in in_list:
        if element[1] > threshold * total:
            filtered.append((element[0] + ' ' + word, element[1]))
        else:
            break
            
    out_list = model[word_type][word]['out'].items()
    out_list.sort(key=lambda x: -x[1])
    total = sum([x[1] for x in out_list])
    for element in out_list:
        if element[1] > threshold * total:
            filtered.append((word + ' ' + element[0], element[1]))
        else:
            break
    
    return filtered
 
# get tweets 
today = int(time() / 86400) * 86400
tweets = []
values = {
 'format': 'json',
 'count': 100,
 'apikey': 'you\'l have to get your own apy key'
 'since': today - 1 * 86400,
 'until': today,
 'q': 'iphone',
 'generator':'twitter',
 'format':'json',
 'language':'english',
}
tweets.extend(get_tweets(values))
texts = [t['content'] for t in tweets]

# apply stemming, POS
texts2 = [tag_and_filter(t) for t in texts]

# parse sentences
nouns_verbs, verbs_nouns = nouns_and_verbs(texts2)

# create model
model = {
 'who': {},
 'what': {},
}
update_model(model, nouns_verbs, verbs_nouns)

# Get top pairs and check them out
results = []
for word in model['what'].iterkeys():
  results.extend(get_links(model, word, 'what'))
results.sort(key=lambda x: -x[1])
