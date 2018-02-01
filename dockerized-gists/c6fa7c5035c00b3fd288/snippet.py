'''
  Project Euler problem 477
  url: https://projecteuler.net/problem=477
'''
import sys

def sequence_gen(n):
    ret = 0
    i   = 0
    while i < n:
        yield ret
        ret = ((ret**2) + 45) % 1000000007
        i += 1

def get_n(n):
    return [i for i in sequence_gen(n)].pop()

def _pop_index(seq):
    if seq[0] >= seq[-1]:
        return 0
    else:
        return -1

def _score_move(seq, move = 0):
    score = 0
    # move is either 0 or -1
    sequence = list(seq)
    score += sequence.pop(move)
    while len(sequence) > 0:
        # opponent move
        score -= sequence.pop(_pop_index(sequence))
        if len(sequence) > 0:
        # self move
            score += sequence.pop(_pop_index(sequence))
    return score

def score(seq):
    # score a is the score for the 0th element
    score_a = 0
    # score b is the score for the -1th element
    score_b = 0
    # start by trying the first element
    score_a = _score_move(seq, 0)
    # then try the last element
    score_b = _score_move(seq, -1)
    #debugging
    print "score_a: %i \nscore_b: %i" % (score_a, score_b)
    if score_a >= score_b:
        return 0
    else:
        return -1

def solve(n):
    p1_score = 0
    p2_score = 0
    seq = [num for num in sequence_gen(n)]
    while len(seq) > 0:
        # player 1 moves
        p1_score += seq.pop(score(seq))
        if len(seq) > 0:
            # player 2 moves
            p2_score += seq.pop(score(seq))
    return p1_score, p2_score

if __name__ == '__main__':
    if len(sys.argv) > 1:
        r = solve(int(sys.argv[1]))
        print "player 1 score: %i" % r[0]
        print "player 2 score: %i" % r[1]
