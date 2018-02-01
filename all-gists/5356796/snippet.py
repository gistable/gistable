import random
from markov import MarkovGenerator
from markov_by_char import CharacterMarkovGenerator

# word MarkovGenerator
generator = MarkovGenerator(n=2, max=500)

# character MarkovGenerator
#generator = CharacterMarkovGenerator(n=3, max=100)

for line in open('white-album.txt'):
  line = line.strip()
  generator.feed(line)
  generator.feed(line)
  
for line in open('black-album.txt'):
  line = line.strip()
  generator.feed(line)

for i in range(3):
    print generator.generate()