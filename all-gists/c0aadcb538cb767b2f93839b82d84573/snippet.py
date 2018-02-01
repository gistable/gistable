"""
"oh hell!" card game logic
(aka contract whilst)
benjamin yates & dave renne, 2016

renne house rules edition
"""
import sys
import random
from itertools import chain

CLUBS = 'CLUBS'
HEARTS = 'HEARTS'
SPADES = 'SPADES'
DIAMONDS = 'DIAMONDS'

SUITS = (CLUBS, HEARTS, SPADES, DIAMONDS)
CARDS = ('2', '3', '4', '5', '6', '7', '8', '9', '10',
         'JACK', 'QUEEN', 'KING', 'ACE')

CHARS = '123456789'

out = sys.stdout.write


def main():
    # clockwise winding
    who = [
        Player('Dave'),
        Player('Ben'),
        Player('Dan'),
    ]
    max_level = min(52 / len(who), 8)

    def order_players(first_idx):
        """make a rotation of the players array so first_idx plays first"""
        return who[first_idx:len(who)] + who[0:first_idx]

    for round_, level in games(max_level):

        print '------------------- begin round {} ------------------------'.format(round_ +1)

        starting_player = round_ % len(who)
        print 'Starting player is', who[starting_player].name

        players = order_players(starting_player)


        # shuffle & deal cards to players
        deck = make_deck()
        for _ in range(level):
            for player in players:
                draw = deck.pop(0)
                player.give_card_to_player(draw)

        # next card from the deck is the trump suit card
        trump_card = deck.pop(0)

        print
        print
        print '------ the trump suit is >>>> {} <<<< ------'.format(trump_card.suit)
        print
        print

        # show players their cards and take bids
        for idx, player in enumerate(players):
            bid = player.view_cards_and_bid()
            players[idx].bid = bid

        # play all of the tricks
        for trick in range(level):
            print 'Trick #', trick

            # play the trick
            board = []
            for player in players:
                card = player.view_cards_and_place(board[0].suit if board else None)
                board.append(card)
                for card in board:
                    out(card.to_str())
                    out('   ')

                state = calc_trick(len(players), trump_card.suit, board)
                print 

            # give winner the trick
            winner_idx = state['winner']
            winner = players[winner_idx]
            print 'Trick goes to ', winner.name
            winner.tricks += 1

            # winner of trick plays first next
            players = order_players(winner_idx)

        # accumulate score for this round
        for player in players:
            if player.bid == player.tricks:
                round_score = 10 + player.tricks
            else:
                round_score = 0
            player.score += round_score
        
        print '------------------- end of round ------------------------'
        print
        print
        print
        print


    print 'holy shit that was fun'
    for player in who:
        print player.name, 'score:', player.score


def make_deck():
    """
    create a shuffled deck of 52 cards

    Returns:
        list of 52 Cards
    """
    def deck_of_cards():
        for suit in SUITS:
            for card in CARDS:
                yield Card(suit, card)

    deck = list(deck_of_cards())
    random.shuffle(deck)
    return deck


def games(max_level):
    """
    Generate the rounds of a game based on the max level desired

    Args:
        max_level: highest number of cards to play

    Yields:
        tuple of round# & number of cards
    """
    ramp_up = xrange(1, max_level + 1)
    ramp_down = xrange(max_level - 1, 0, -1)
    up_and_down = chain(ramp_up, ramp_down)
    return enumerate(up_and_down)


class Card(object):
    def __init__(self, suit, value):
        assert suit in (CLUBS, HEARTS, SPADES, DIAMONDS)
        assert value in CARDS
        self.suit = suit
        self.value = value

    def __repr__(self):
        return '<Card suit="{}" value="{}">'.format(self.suit, self.value)

    def to_str(self):
        return '<{} of {}>'.format(self.value, self.suit)



def card_value(card_name):
    """
    Convert a card string to a numeric value for compraisons

    Args:
        card_name: name of card

    Returns:
        integer value for comparing cards
    """
    assert card_name in CARDS
    return CARDS.index(card_name)


class Player(object):
    def __init__(self, name):
        self.name = name
        self.cards = []
        self.tricks = 0
        self.bid = 0
        self.score = 0
    
    def give_card_to_player(self, card):
        self.cards.append(card)

    def view_cards_and_place(self, preferred=None):

        if preferred:
            available = [card for card in self.cards if card.suit == preferred]
            if not available:
                available = self.cards
        else:
            available = self.cards

        print self.name, 'chooses a card:'
        out('     ')
        for idx, card in enumerate(available):
            out(CHARS[idx])
            out(': ')
            out(card.to_str())
            out('  ')
        print

        out('Choose >>> ')
        choice = sys.stdin.readline().strip()
        idx = CHARS.index(choice)

        chosen_card = available[idx]
        
        card = self.cards.pop(self.cards.index(chosen_card))
        print self.name, 'places a', str(card)
        print
        print
        print
        return card

    def view_cards_and_bid(self):
        print self.name, 'Your cards:'
        out('     ')
        for idx, card in enumerate(self.cards):
            out(card.to_str())
            out('  ')
        print

        out('Bid >>> ')
        choice = int(sys.stdin.readline().strip())
        return choice


def calc_trick(players, trump_suit, played_cards):
    """
    compute the state of the trick/game given
    the state of the board

    Args:
        players: number of players
        trump_suit: trump suit!
        played_cards: array of cards played so far

    Returns:
        dict describing the state of the game
    """
    def cmp_lt(lead_suit, trump_suit, a, b):
        """compare cards a & b, given trump & lead suit"""

        def cmp_lt_card(a, b):
            """compare card values"""
            return card_value(a.value) < card_value(b.value)

        # order-dependent sieve
        if a.suit == trump_suit and b.suit == trump_suit:
            return cmp_lt_card(a, b)
        elif a.suit == trump_suit:
            return False
        elif b.suit == trump_suit:
            return True
        elif a.suit == lead_suit and b.suit == lead_suit:
            return cmp_lt_card(a, b)
        elif a.suit == lead_suit:
            return False
        elif b.suit == lead_suit:
            return True
        else:
            return cmp_lt_card(a, b)

    if not played_cards:
        return {'state': 'WAITING_FOR_PLAYER', 'player': 0}

    # lead suit comes from the first placed card
    lead_suit = played_cards[0].suit

    # find the maximum card/player
    # start with the first card as the winner
    # and compare with each subsequent card,
    # swapping if we find a higher card
    plays = enumerate(played_cards)
    winner = next(plays)
    for player_id, card in plays:
        winner_is_less = cmp_lt(lead_suit, trump_suit, winner[1], card)
        if winner_is_less:
            winner = (player_id, card)

    if len(played_cards) == players:
        return {'state': 'GAME_OVER',
                'winner': winner[0]}
    else:
        return {'state': 'WAITING_FOR_PLAYER',
                'player': len(played_cards),
                'winner': winner[0],
                'lead_suit': lead_suit}


if __name__ == '__main__':
    main()