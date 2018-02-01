import nltk
import random

STOP_WORDS = ['the', 'a', 'and', 'of', 'in', 'with', 'for', 'on']

def rhyme(inp, level):
  entries = nltk.corpus.cmudict.entries()
  syllables = [(word, syl) for word, syl in entries if word == inp]
  rhymes = []
  for (word, syllable) in syllables:
    rhymes += [word for word, pron in entries if pron[-level:] == syllable[-level:]]
    return set(rhymes)

def quirk(sent):
  words = nltk.word_tokenize(sent)
  for word in words:
    if word.lower() in STOP_WORDS or random.randint(1, 100) > 80:
      continue

    rhymes = rhyme(word, 2)
    if rhymes:
      r = random.sample(rhymes, 1).pop()
      sent = sent.replace(word, r)
  print(sent)
