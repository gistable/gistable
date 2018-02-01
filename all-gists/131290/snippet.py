from __future__ import with_statement
import random
 
def create_chain(file_paths):
    markov_chain = {}
    word1 = "\n"
    word2 = "\n"
    for path in file_paths:
        with open(path) as file:
            for line in file:
                for current_word in line.split():
                    if current_word != "":
                        markov_chain.setdefault((word1, word2), []).append(current_word)
                        word1 = word2
                        word2 = current_word
    return markov_chain
 
def construct_sentence(markov_chain, word_count=30):
    generated_sentence = ""
    word_tuple = random.choice(markov_chain.keys())
    w1 = word_tuple[0]
    w2 = word_tuple[1]
    
    for i in xrange(word_count):
        #"total count" is a special key used to track word frequency.
        newword = random.choice(markov_chain[(w1, w2)])
        generated_sentence = generated_sentence + " " + newword
        w1 = w2
        w2 = newword
        
    return generated_sentence
 
markov = create_chain(
                      (
                       "/users/darkxanthos/documents/workspace/markovchain/src/documents/shanechat.txt",
                       "/users/darkxanthos/documents/workspace/markovchain/src/documents/bible.txt",
                       "/users/darkxanthos/documents/workspace/markovchain/src/documents/arabiannights.txt",
                       "/users/darkxanthos/documents/workspace/markovchain/src/documents/alice.txt",
                       "/users/darkxanthos/documents/workspace/markovchain/src/documents/taoteching.txt",
                       "/users/darkxanthos/documents/workspace/markovchain/src/documents/communist_manifesto.txt",
                       "/users/darkxanthos/documents/workspace/markovchain/src/documents/portrait.txt",
                       "/users/darkxanthos/documents/workspace/markovchain/src/documents/ulysses.txt",
                       "/users/darkxanthos/documents/workspace/markovchain/src/documents/dubliners.txt",
                       ))
#print markov
print construct_sentence(markov_chain = markov, word_count=100)