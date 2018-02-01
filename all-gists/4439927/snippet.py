import re, random
  
def shuffle_one(word):
  if len(word) <= 3:
    return word
   
  middle = list(word[1:-1])
  random.shuffle(middle)
    
  return word[0] + ''.join(middle) + word[-1]
  
def repl(match):
  return shuffle_one(match.groups()[0])
  
def shuffle(text):
  return re.sub("(\w+)", repl, text)
  
shuffle("Normally, reading this shouldn't be too hard.")
