from __future__ import print_function
from random import shuffle, seed
from itertools import product
from collections import Counter

#seed(100)
ranks = list('23456789TJQKA')
alt_ranks = list('A23456789TJQK')
suits = list('CSHD')
new_deck = list(product(ranks, suits))
assert len(new_deck)==52
total_num_hands = 48


def score_hand(hand):
    """Given a hand, e.g., ["AC","KD","4D","4C","TH"], return 
    a sortable score tuple: (1, 2, 12, 11, 8)
    a description of the hand: ['Pair', '4', 'A', 'K', 'T']
    Totally Norvigy"""
    hranks, hsuits = zip(*hand)
    
    #-------------------------------------------------------------------------------------
    # First check if it's a flush or a straight
    #
    is_flush = True if len(set(hsuits)) == 1 else False
    
    is_straight = False
    def min_max_range(l): return max(l) - min(l)
    if (len(set(hranks)) == 5 and 
        (min_max_range(sorted(map(ranks.index, hranks))) == 4 or 
         min_max_range(sorted(map(alt_ranks.index, hranks))) == 4)):
       is_straight = True
    
    #-------------------------------------------------------------------------------------
    # Then check if it's n-of-a-kind (pair, three, four, full house...)
    # Sort cards, first by count, then high card down to low card
    #
    rank_counter = [(hranks.count(rank), rank) for rank in ranks]
    rank_counter.sort(key=lambda x: (-x[0], -ranks.index(x[1])) )
    
    is_n_of_a_kind = {2:False, 3:False, 4:False}
    main_cards, high_cards = [], [] # cards that group vs just high cards
    max_count, max_rank = rank_counter.pop(0)
    
    if max_count == 4:
        is_n_of_a_kind[4] = True
        main_cards.append(max_rank)
        max_count, max_rank = rank_counter.pop(0)
    elif max_count == 3:
        is_n_of_a_kind[3] = True
        main_cards.append(max_rank)        
        max_count, max_rank = rank_counter.pop(0)
        
        if max_count == 2: # full house
            main_cards.append(max_rank)
    elif max_count == 2:
        is_n_of_a_kind[2] = True
        main_cards.append(max_rank)        
        max_count, max_rank = rank_counter.pop(0)
        
        if max_count == 2: # two pair
            main_cards.append(max_rank)
            max_count, max_rank = rank_counter.pop(0)
    
    while max_count == 1:
        high_cards.append(max_rank)
        max_count, max_rank = rank_counter.pop(0)
    
    # The one special case where the high card is not the ranks.index
    # Move the Ace to the end of the list since it's now the low card
    if set(hranks) == set("A2345"):
        assert high_cards[0]=="A" and high_cards[1]=="5"
        high_cards.append(high_cards.pop(0))
    
    #-------------------------------------------------------------------------------------
    # Map my hand onto a hand-type and a score tuple
    #
    hand_map = [
        (is_flush and is_straight and high_cards[0] == "A", "Royal Straight Flush"),
        (is_flush and is_straight,                          "Straight Flush"),
        (is_n_of_a_kind[4],                                 "Four of a Kind"),
        (is_n_of_a_kind[3] and is_n_of_a_kind[2],           "Full House"),
        (is_flush,                                          "Flush"),
        (is_straight,                                       "Straight"),
        (is_n_of_a_kind[3],                                 "Three of a Kind"),
        (is_n_of_a_kind[2] and len(main_cards)==2,          "Two Pair"),
        (is_n_of_a_kind[2],                                 "Pair"),
        (True,                                              "High Card")
    ]
    hand_order = list(reversed([h[1] for h in hand_map]))
    
    hand_type = next(h[1] for h in hand_map if h[0] is True)
    hand_ranks = main_cards + high_cards
    hand_desc = [hand_type] + hand_ranks
    
    def hand_to_score_tuple(hand_type, hand_cards):
        """Produce a tuple where if a>b, a is a better hand than b"""
        return tuple([hand_order.index(hand_type)] + 
                     [ranks.index(rank) for rank in hand_ranks])
    
    return hand_to_score_tuple(hand_type, hand_ranks), hand_desc


def run(N, process_num=0, multi_probs=None, multi_secretary=None):
    """Make a table that tells me the probability that i have the top hand
    e.g., [0]("High Card", "6") -> 0% chance
          [46]("Royal Straight Flush", "A") -> 100% chance
    """
    def calc_secretary(_hand_scores, _best_hand, secretary):
        # Secretary problem: when should i stop?
        best_score_first_n = -1
        for sn1 in range(len(_hand_scores)):
            if _hand_scores[sn1]['hand_score'] > best_score_first_n:
                best_score_first_n = _hand_scores[sn1]['hand_score']
            
            for sn2 in range(sn1+1, len(_hand_scores)):
                if _hand_scores[sn2]['hand_score'] > best_score_first_n:
                    if _hand_scores[sn2] == _best_hand:
                        secretary[sn1][0] += 1
                    else:
                        secretary[sn1][1] += 1
                    break
            else:
                secretary[sn1][1] += 1
        return
    
    deck = new_deck[:]
    
    probs = {n:{} for n in range(total_num_hands)}
    secretary = {n:[0,0] for n in range(total_num_hands)}
    
    for _ in range(N):
        shuffle(deck)
        
        hands = [deck[n:n+5] for n in range(len(deck)-4)]
        assert len(hands) == total_num_hands
        
        hand_scores = []
        for handn, hand in enumerate(hands):
            hand_score, hand_desc = score_hand(hand)
            hand_scores.append( {"hand_score": hand_score, "hand_desc":hand_desc, 
                                 "hand":hand, "handn":handn} )
        
        sorted_hand_scores = sorted(hand_scores, reverse=True, key=lambda x: x['hand_score'])
        best_hand = sorted_hand_scores[0]
        
        calc_secretary(hand_scores, best_hand, secretary)
        
        for _n, hand_score in enumerate(hand_scores):
            h = tuple(hand_score['hand_desc'][0:2])
            handn = hand_score['handn']
            assert handn==_n
            
            # If there is a better hand ahead
            if any(hand_scores[_n]['hand_score'] > hand_score['hand_score'] 
                   for _n in range(n+1, total_num_hands)):
                if h not in probs[n]:
                    probs[n][h] = [1, 0]
                else:
                    probs[n][h][0] += 1
                #break
            else:
                if h not in probs[n]:
                    probs[n][h] = [0, 1]
                else:
                    probs[n][h][1] += 1
    
    if multi_probs is not None:
        multi_probs[process_num] = probs
        multi_secretary[process_num] = secretary
    else:
        return probs, secretary


def convert_to_lua_table(fname):
    """From pokerchicken.lua:
    local hand_map = {[1]="High Card", [2]="Pair", [3]="Two Pair", 
                  [4]="Three of a Kind", [5]="Straight", [6]="Flush", 
                  [7]="Full House", [8]="Four of a Kind", [9]="Straight Flush"}
    """
    lua_map = {"High Card":1, "Pair":2, "Two Pair":3, "Three of a Kind":4, "Straight":5,
               "Flush":6, "Full House":7, "Four of a Kind":8, "Straight Flush":9,
               "Royal Straight Flush":9}
    
    d = eval(open(fname).read())
    ld = []
    for hand_type in sorted(lua_map):
        for rank in ranks:
            ld.append([lua_map[hand_type]])
            #ld.append([hand_type]) # to see what's going on...
            ld[-1].append(rank)
            for n in range(total_num_hands):
                if (hand_type, rank) in d[n]:
                    vals = d[n][(hand_type, rank)]
                    ld[-1].append(float(vals[1]) / (vals[0] + vals[1]))
                else:
                    ld[-1].append(-1)
    
    out = open("stats.lua", 'w')
    out.write("local M={")
    for row in ld:
        out.write('["%s_%s"]={' % (row[0], row[1]))
        out.write(','.join("%.3g" % n for n in row[2:]))
        out.write("},\n")
    out.write("}\nreturn M\n")


def plot_secretary(secretary):
    from matplotlib import pyplot
    import math
    pyplot.figure()
    pyplot.plot([t[0]/(t[1]+.1) for t in secretary.values()])
    pyplot.axvline(x=total_num_hands/math.e, ymin=0, ymax=1)
    pyplot.savefig("secretary.png")

#-----------------------------------------------------------------------------------------
# Mains
#
def main(iters):
    from pprint import pprint
    probs, secretary = run(iters)
    pprint(probs)
    
    plot_secretary(secretary)

def multi_main(num_processes, iters):
    import multiprocessing
    from pprint import pprint
    from copy import copy, deepcopy
    manager = multiprocessing.Manager()
    multi_probs = manager.dict()
    multi_secretary = manager.dict()
    
    procs = []
    for process_num in range(num_processes):
        procs.append(multiprocessing.Process(target=run, args=(iters, process_num, 
            multi_probs, multi_secretary)))
    for p in procs: p.start()
    for p in procs: p.join()
    
    # Combine results from all my processes into one dictionary
    probs = deepcopy(dict(multi_probs[0]))
    for process_num in range(1, num_processes):
        mprobs = multi_probs[process_num]
        for handn in mprobs:
            for hand_type in mprobs[handn]:
                if hand_type not in probs[handn]:
                    probs[handn][hand_type] = copy(mprobs[handn][hand_type])
                else:
                    probs[handn][hand_type][0] += mprobs[handn][hand_type][0]
                    probs[handn][hand_type][1] += mprobs[handn][hand_type][1]
    
    pprint(probs)

if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("mode")
    args = parser.parse_args()
    
    if args.mode == "main":
        main(int(1e5))
    elif args.mode == "multi":
        import multiprocessing
        use_cpus = multiprocessing.cpu_count()-3
        multi_main(use_cpus, int(1e7)/use_cpus)
    elif args.mode == "lua":
        convert_to_lua_table("multi_main4.out")
    else:
        print("Bad argument: {}".format(args.mode))