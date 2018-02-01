# coding: utf-8

# ## IPython Notebook for [Bommarito Consulting](http://bommaritollc.com/) Blog Post
# 
# ### **Link**: [Fuzzy sentence matching in Python](http://bommaritollc.com/2014/06/fuzzy-match-sentences-in-python): http://bommaritollc.com/2014/06/fuzzy-match-sentences-in-python
# 
# **Author**: [Michael J. Bommarito II](https://www.linkedin.com/in/bommarito/)

# In[159]:

# Imports
import difflib
import nltk


# In[160]:

target_sentence = "In the eighteenth century it was often convenient to regard man as a clockwork automaton."

sentences = ["In the eighteenth century it was often convenient to regard man as a clockwork automaton.",
             "in the eighteenth century    it was often convenient to regard man as a clockwork automaton",
             "In the eighteenth century, it was often convenient to regard man as a clockwork automaton.",
             "In the eighteenth century, it was not accepted to regard man as a clockwork automaton.",
             "In the eighteenth century, it was often convenient to regard man as clockwork automata.",
             "In the eighteenth century, it was often convenient to regard man as clockwork automatons.",
             "It was convenient to regard man as a clockwork automaton in the eighteenth century.",
             "In the 1700s, it was common to regard man as a clockwork automaton.",
             "In the 1700s, it was convenient to regard man as a clockwork automaton.",
             "In the eighteenth century.",
             "Man as a clockwork automaton.",
             "In past centuries, man was often regarded as a clockwork automaton.",
             "The eighteenth century was characterized by man as a clockwork automaton.",
             "Very long ago in the eighteenth century, many scholars regarded man as merely a clockwork automaton.",]


# ## Example 1 - Exact Match

# In[161]:

def is_exact_match(a, b):
    """Check if a and b are matches."""
    return (a == b)

for sentence in sentences:
    print(is_exact_match(target_sentence, sentence), sentence)


# ## Example 2 - Exact Case-Insensitive Token Match after Stopwording

# In[162]:

# Imports
import nltk.corpus
import nltk.tokenize.punkt
import string

# Get default English stopwords and extend with punctuation
stopwords = nltk.corpus.stopwords.words('english')
stopwords.extend(string.punctuation)

# Create tokenizer
tokenizer = nltk.tokenize.punkt.PunktWordTokenizer()

def is_ci_token_stopword_match(a, b):
    """Check if a and b are matches."""
    tokens_a = [token.lower().strip(string.punctuation) for token in tokenizer.tokenize(a)                     if token.lower().strip(string.punctuation) not in stopwords]
    tokens_b = [token.lower().strip(string.punctuation) for token in tokenizer.tokenize(b)                     if token.lower().strip(string.punctuation) not in stopwords]

    return (tokens_a == tokens_b)

for sentence in sentences:
    print(is_ci_token_stopword_match(target_sentence, sentence), sentence)


# ## Example 3 - Exact Token Match after Stopwording and Stemming

# In[163]:

# Imports
import nltk.corpus
import nltk.tokenize.punkt
import nltk.stem.snowball
import string

# Get default English stopwords and extend with punctuation
stopwords = nltk.corpus.stopwords.words('english')
stopwords.extend(string.punctuation)

# Create tokenizer and stemmer
tokenizer = nltk.tokenize.punkt.PunktWordTokenizer()
stemmer = nltk.stem.snowball.SnowballStemmer('english')

def is_ci_token_stopword_stem_match(a, b):
    """Check if a and b are matches."""
    tokens_a = [token.lower().strip(string.punctuation) for token in tokenizer.tokenize(a)                     if token.lower().strip(string.punctuation) not in stopwords]
    tokens_b = [token.lower().strip(string.punctuation) for token in tokenizer.tokenize(b)                     if token.lower().strip(string.punctuation) not in stopwords]
    stems_a = [stemmer.stem(token) for token in tokens_a if len(token) > 0]
    stems_b = [stemmer.stem(token) for token in tokens_b if len(token) > 0]

    return (stems_a == stems_b)

for sentence in sentences:
    print(is_ci_token_stopword_stem_match(target_sentence, sentence), sentence)


# ## Example 4 - Exact Token Match after Stopwording and Lemmatizing

# In[164]:

# Imports
import nltk.corpus
import nltk.tokenize.punkt
import nltk.stem.snowball
import string

# Get default English stopwords and extend with punctuation
stopwords = nltk.corpus.stopwords.words('english')
stopwords.extend(string.punctuation)

# Create tokenizer and stemmer
tokenizer = nltk.tokenize.punkt.PunktWordTokenizer()
lemmatizer = nltk.stem.wordnet.WordNetLemmatizer()

def is_ci_token_stopword_lemma_match(a, b):
    """Check if a and b are matches."""
    tokens_a = [token.lower().strip(string.punctuation) for token in tokenizer.tokenize(a)                     if token.lower().strip(string.punctuation) not in stopwords]
    tokens_b = [token.lower().strip(string.punctuation) for token in tokenizer.tokenize(b)                     if token.lower().strip(string.punctuation) not in stopwords]
    stems_a = [lemmatizer.lemmatize(token) for token in tokens_a if len(token) > 0]
    stems_b = [lemmatizer.lemmatize(token) for token in tokens_b if len(token) > 0]

    return (stems_a == stems_b)

for sentence in sentences:
    print(is_ci_token_stopword_lemma_match(target_sentence, sentence), sentence)


# ## Example 5 - Partial Sequence Match after Stopwording and Lemmatizing

# In[166]:

# Imports
import nltk.corpus
import nltk.tokenize.punkt
import nltk.stem.snowball
import string

# Get default English stopwords and extend with punctuation
stopwords = nltk.corpus.stopwords.words('english')
stopwords.extend(string.punctuation)

# Create tokenizer and stemmer
tokenizer = nltk.tokenize.punkt.PunktWordTokenizer()
lemmatizer = nltk.stem.wordnet.WordNetLemmatizer()

def is_ci_partial_seq_token_stopword_lemma_match(a, b):
    """Check if a and b are matches."""
    tokens_a = [token.lower().strip(string.punctuation) for token in tokenizer.tokenize(a)                     if token.lower().strip(string.punctuation) not in stopwords]
    tokens_b = [token.lower().strip(string.punctuation) for token in tokenizer.tokenize(b)                     if token.lower().strip(string.punctuation) not in stopwords]
    stems_a = [lemmatizer.lemmatize(token) for token in tokens_a if len(token) > 0]
    stems_b = [lemmatizer.lemmatize(token) for token in tokens_b if len(token) > 0]

    # Create sequence matcher
    s = difflib.SequenceMatcher(None, stems_a, stems_b)
    return (s.ratio() > 0.66)

for sentence in sentences:
    print(is_ci_partial_seq_token_stopword_lemma_match(target_sentence, sentence), sentence)


# ## Example 6 - Partial Set Match after Stopwording and Lemmatizing

# In[167]:

# Imports
import nltk.corpus
import nltk.tokenize.punkt
import nltk.stem.snowball
import string

# Get default English stopwords and extend with punctuation
stopwords = nltk.corpus.stopwords.words('english')
stopwords.extend(string.punctuation)

# Create tokenizer and stemmer
tokenizer = nltk.tokenize.punkt.PunktWordTokenizer()
lemmatizer = nltk.stem.wordnet.WordNetLemmatizer()

def is_ci_partial_set_token_stopword_lemma_match(a, b):
    """Check if a and b are matches."""
    tokens_a = [token.lower().strip(string.punctuation) for token in tokenizer.tokenize(a)                     if token.lower().strip(string.punctuation) not in stopwords]
    tokens_b = [token.lower().strip(string.punctuation) for token in tokenizer.tokenize(b)                     if token.lower().strip(string.punctuation) not in stopwords]
    stems_a = [lemmatizer.lemmatize(token) for token in tokens_a if len(token) > 0]
    stems_b = [lemmatizer.lemmatize(token) for token in tokens_b if len(token) > 0]

    # Calculate Jaccard similarity
    ratio = len(set(stems_a).intersection(stems_b)) / float(len(set(stems_a).union(stems_b)))
    return (ratio > 0.66)

for sentence in sentences:
    print(is_ci_partial_set_token_stopword_lemma_match(target_sentence, sentence), sentence)


# ## Example 7 - Partial Noun Set Match after Stopwording and Lemmatizing

# In[168]:

# Imports
import nltk.corpus
import nltk.tokenize.punkt
import nltk.stem.snowball
import string

# Get default English stopwords and extend with punctuation
stopwords = nltk.corpus.stopwords.words('english')
stopwords.extend(string.punctuation)

# Create tokenizer and stemmer
tokenizer = nltk.tokenize.punkt.PunktWordTokenizer()
lemmatizer = nltk.stem.wordnet.WordNetLemmatizer()

def is_ci_partial_noun_set_token_stopword_lemma_match(a, b):
    """Check if a and b are matches."""
    pos_a = nltk.pos_tag(tokenizer.tokenize(a))
    pos_b = nltk.pos_tag(tokenizer.tokenize(b))
    tokens_a = [token.lower().strip(string.punctuation) for token, pos in pos_a                     if pos.startswith('N') and (token.lower().strip(string.punctuation) not in stopwords)]
    tokens_b = [token.lower().strip(string.punctuation) for token, pos in pos_b                     if pos.startswith('N') and (token.lower().strip(string.punctuation) not in stopwords)]
    stems_a = [lemmatizer.lemmatize(token) for token in tokens_a if len(token) > 0]
    stems_b = [lemmatizer.lemmatize(token) for token in tokens_b if len(token) > 0]

    # Calculate Jaccard similarity
    ratio = len(set(stems_a).intersection(stems_b)) / float(len(set(stems_a).union(stems_b)))
    return (ratio > 0.66)

for sentence in sentences:
   print(is_ci_partial_noun_set_token_stopword_lemma_match(target_sentence, sentence), sentence)
