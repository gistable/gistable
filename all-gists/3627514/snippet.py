import random, sys

NONWORD = "\n"
STARTKEY = NONWORD, NONWORD
MAXGEN=1000

class MarkovChainer(object):
    def __init__(self):
        self.state = dict()

    def input(self, input):
        word1, word2 = STARTKEY
        for word3 in input.split():
            self.state.setdefault((word1, word2), list()).append(word3)
            word1, word2 = word2, word3 
        self.state.setdefault((word1, word2), list()).append(NONWORD)

    def output(self):
        output = list()
        word1, word2 = STARTKEY
        for i in range(MAXGEN):
            word3 = random.choice(self.state[(word1,word2)])
            if word3 == NONWORD: break
            output.append(word3)
            word1, word2 = word2, word3
        return " ".join(output)

if __name__ == "__main__":
    c = MarkovChainer()
    c.input(sys.stdin.read())
    print c.output()
