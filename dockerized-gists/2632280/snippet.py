#!/usr/bin/python
#

import sys
import os
import copy
import random

deck = [1,2,3,4,5,6,7,8,9,0,0,0,0]
deck = [1,2,3,4,5,6,7,8,9,0,0,0,0]
results = {
    'bank': 0,
    'player': 0,
    'tie': 0,
}


def generate_deck(n=1):
    decks = deck * 4 * n
    random.shuffle(decks)
    return decks

def simulate_game(decks):
    player = [decks.pop()]
    bank = [decks.pop()]
    player.append(decks.pop())
    bank.append(decks.pop())

    player_score = sum(player) % 10
    bank_score = sum(bank) % 10
    if player_score >= 8 or bank_score >= 8:
        if player_score > bank_score:
            return 'player'
        elif bank_score > player_score:
            return 'bank'
        else:
            return 'tie'

    # player draws 3rd card
    if player_score <= 5:
        pcard = decks.pop()
        player.append(pcard)
        # bank rules
        if pcard in (2,3) and bank_score <= 4:
            bank.append(decks.pop())
        elif pcard in (4,5) and bank_score <= 5:
            bank.append(decks.pop())
        elif pcard in (6,7) and bank_score <= 6:
            bank.append(decks.pop())
        elif pcard == 8 and bank_score <= 2:
            bank.append(decks.pop())
        elif pcard in (1,9,0) and bank_score <= 3:
            bank.append(decks.pop())
    elif bank_score <= 5:
        bank.append(decks.pop())

    player_score = sum(player) % 10
    bank_score = sum(bank) % 10
    if player_score == bank_score:
        return 'tie'
    return 'player' if player_score > bank_score else 'bank'


def main():
    for i in range(3000):
        # 3000 game / 8 decks of cards each
        decks = generate_deck(8)
        while len(decks) > 10:
            winner = simulate_game(decks)
            results[winner] += 1

    total = results['player'] + results['bank'] + results['tie']
    print "Baccarat probabilties"
    print 'P(win|player)', results['player'] / float(total)
    print 'P(win|bank)  ', results['bank'] / float(total)
    print 'P(tie)       ', results['tie'] / float(total)


if __name__=="__main__":
    main()
