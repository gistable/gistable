#!/usr/bin/env python
# let's cheat at scrabble

def count_letters(word):
  count = {} 
  for letter in word:
    if letter not in count: count[letter] = 0
    count[letter] += 1 
  return count 

def spellable(word, rack):
    word_count = count_letters(word)
    rack_count  = count_letters(rack)
    return all( [word_count[letter] <= rack_count[letter] for letter in word] )  

score = {"a": 1, "c": 3, "b": 3, "e": 1, "d": 2, "g": 2, 
         "f": 4, "i": 1, "h": 4, "k": 5, "j": 8, "m": 3, 
         "l": 1, "o": 1, "n": 1, "q": 10, "p": 3, "s": 1, 
         "r": 1, "u": 1, "t": 1, "w": 4, "v": 4, "y": 4, 
         "x": 8, "z": 10}

def score_word(word):
  # http://www.xwordinfo.com/Scrabble/HighestDaily
  return sum([score[c] for c in word])

def word_reader(filename):
  # returns an iterator
  return (word.strip() for word in  open(filename)) 

if __name__ == "__main__":
  import sys
  if len(sys.argv) == 2: 
    rack = sys.argv[1].strip()
  else:
    print """Usage: python cheat_at_scrabble.py <yourrack>"""
    exit()

  words = word_reader('/usr/share/dict/words')
  scored =  ((score_word(word), word) for word in words if set(word).issubset(set(rack)) and len(word) > 1 and spellable(word, rack))
  
  for score, word in sorted(scored):
    print str(score), '\t', word

