from random import shuffle

def trial():
    # Deck comprised of 30 cards, two of each. Assume:
    # 0=Lightwarden, 1=CoH, 2=Pyromancer, 3=Silence
    deck = range(15) + range(15)
    shuffle(deck)

    # Initial 4 draws
    hand = [deck.pop() for i in range(4)]

    # You need both 0 on turn 1
    # You need both 1 by turn 2
    # You need one of 2 and 3 by turn 2
    to_draw = 0
    new_hand = []
    for index, card in enumerate(hand):
        # Card we don't care about, or duplicate of 2/3
        if card > 3 or (card in [2, 3] and hand.index(card) < i):
            to_draw += 1
            deck.append(card)
        else:
            new_hand.append(card)

    hand = new_hand

    # Shuffle deck again
    shuffle(deck)

    # Muligan draw + 1 turn draw
    for i in range(to_draw + 1):
        hand.append(deck.pop())

    # Check if we have 2 Lightwarden
    if hand.count(0) < 2:
        return False

    # Draw
    hand.append(deck.pop())

    # Check if we have 2 CoH
    if hand.count(1) < 2:
        return False

    # Check if we have Pyromancer
    if 2 not in hand:
        return False

    # Check if we have Silence
    if 3 not in hand:
        return False

    # Success!
    return True

total = 100000000
success = 0
for i in range(total):
    success += trial()

print "{}/{}".format(success, total)