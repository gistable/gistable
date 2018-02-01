import unittest
import collections
from solution import (RANKS, SUITS, Card, CardCollection,
                      StandardDeck, SixtySixDeck, BeloteDeck)


class RankTest(unittest.TestCase):
    def setUp(self):
        self.rank_string = 'Three'
        self.rank = RANKS[self.rank_string]()

    def test_creation(self):
        self.assertTrue(self.rank.__class__.__name__, self.rank_string)

    def test_equality_for_identical_ranks(self):
        rank_copy = RANKS[self.rank_string]()
        self.assertEqual(rank_copy, self.rank)

    def test_equality_for_diffent_ranks(self):
        different_rank = RANKS['Four']()
        self.assertNotEqual(different_rank, self.rank)

    def test_stringify(self):
        self.assertEqual(self.rank_string, str(self.rank))

    def test_symbol_is_there(self):
        self.assertEqual(self.rank.symbol, '3')


class SuitTest(unittest.TestCase):
    def setUp(self):
        self.suit_string = 'Diamonds'
        self.suit = SUITS[self.suit_string]()

    def test_creation(self):
        self.assertTrue(self.suit.__class__.__name__, self.suit_string)

    def test_equality_for_identical_suits(self):
        suit_copy = SUITS[self.suit_string]()
        self.assertEqual(suit_copy, self.suit)

    def test_equality_for_diffent_suits(self):
        different_suit = SUITS['Hearts']()
        self.assertNotEqual(different_suit, self.suit)

    def test_stringify(self):
        self.assertEqual(self.suit_string, str(self.suit))

    def test_color_is_there(self):
        self.assertEqual(self.suit.color, 'red')


class CardTest(unittest.TestCase):
    def setUp(self):
        self.rank = RANKS['Ace']
        self.suit = SUITS['Spades']
        self.card = Card(self.rank, self.suit)

    def test_equality_for_identical_cards(self):
        self.assertEqual(self.card, Card(self.rank, self.suit))

    def test_equality_for_different_cards(self):
        different_card = Card(RANKS['Queen'], SUITS['Diamonds'])
        self.assertNotEqual(different_card, self.card)

    def test_stringify(self):
        self.assertEqual(str(self.card), 'Ace of Spades')


class CardCollectionTest(unittest.TestCase):
    def setUp(self):
        self.collection = [Card(RANKS['Ace'], SUITS['Diamonds']),
                           Card(RANKS['Queen'], SUITS['Spades']),
                           Card(RANKS['Two'], SUITS['Hearts']),
                           Card(RANKS['Seven'], SUITS['Spades']),
                           Card(RANKS['Ace'], SUITS['Diamonds']), ]
        self.deck = CardCollection(self.collection)

    def test_top_card_returns_the_top_card(self):
        self.assertEqual(self.collection[-1], self.deck.top_card())

    def test_bottom_card_returns_the_bottom_card(self):
        self.assertEqual(self.collection[0], self.deck.bottom_card())

    def test_add_card_appends_card_to_deck(self):
        added_card = Card(RANKS['King'], SUITS['Diamonds'])
        self.deck.add(added_card)
        self.assertEqual(self.deck.top_card(), added_card)

    def test_draw_from_top_removes_top_card_and_returns_it(self):
        self.assertEqual(self.deck.draw_from_top(), self.collection[-1])
        self.assertEqual(self.collection[-2], self.deck.top_card())

    def test_draw_from_bottom_removes_bottom_card_and_returns_it(self):
        self.assertEqual(self.deck.draw_from_bottom(), self.collection[0])
        self.assertEqual(self.collection[1], self.deck.bottom_card())

    def test_index_returns_index_of_card(self):
        self.assertEqual(self.deck.index(self.collection[3]), 3)

    def test_index_return_first_occurences_of_card(self):
        self.assertEqual(self.deck.index(self.collection[4]), 0)

    def test_index_throws_value_error_if_item_is_missing(self):
        missing_card = Card(RANKS['Five'], SUITS['Spades'])
        self.assertRaises(ValueError, self.deck.index, missing_card)

    def test_is_iterable(self):
        self.assertIsInstance(self.deck, collections.Iterable)

    def test_is_indexable(self):
        self.assertTrue('__getitem__' in dir(self.deck))


class StandardDecksTest(unittest.TestCase):
    def generate_list_of_cards(self, ranks):
        return []

    def test_standard_deck(self):
        standard_deck = ['King of Diamonds',
                         'Queen of Diamonds',
                         'Jack of Diamonds',
                         'Ten of Diamonds',
                         'Nine of Diamonds',
                         'Eight of Diamonds',
                         'Seven of Diamonds',
                         'Six of Diamonds',
                         'Five of Diamonds',
                         'Four of Diamonds',
                         'Three of Diamonds',
                         'Two of Diamonds',
                         'Ace of Diamonds',
                         'King of Clubs',
                         'Queen of Clubs',
                         'Jack of Clubs',
                         'Ten of Clubs',
                         'Nine of Clubs',
                         'Eight of Clubs',
                         'Seven of Clubs',
                         'Six of Clubs',
                         'Five of Clubs',
                         'Four of Clubs',
                         'Three of Clubs',
                         'Two of Clubs',
                         'Ace of Clubs',
                         'King of Hearts',
                         'Queen of Hearts',
                         'Jack of Hearts',
                         'Ten of Hearts',
                         'Nine of Hearts',
                         'Eight of Hearts',
                         'Seven of Hearts',
                         'Six of Hearts',
                         'Five of Hearts',
                         'Four of Hearts',
                         'Three of Hearts',
                         'Two of Hearts',
                         'Ace of Hearts',
                         'King of Spades',
                         'Queen of Spades',
                         'Jack of Spades',
                         'Ten of Spades',
                         'Nine of Spades',
                         'Eight of Spades',
                         'Seven of Spades',
                         'Six of Spades',
                         'Five of Spades',
                         'Four of Spades',
                         'Three of Spades',
                         'Two of Spades',
                         'Ace of Spades']

        self.assertSequenceEqual([str(card) for card in StandardDeck()],
                                 standard_deck)

    def test_belote_deck(self):
        belotte_deck = ['King of Diamonds',
                        'Queen of Diamonds',
                        'Jack of Diamonds',
                        'Ten of Diamonds',
                        'Nine of Diamonds',
                        'Eight of Diamonds',
                        'Seven of Diamonds',
                        'Ace of Diamonds',
                        'King of Clubs',
                        'Queen of Clubs',
                        'Jack of Clubs',
                        'Ten of Clubs',
                        'Nine of Clubs',
                        'Eight of Clubs',
                        'Seven of Clubs',
                        'Ace of Clubs',
                        'King of Hearts',
                        'Queen of Hearts',
                        'Jack of Hearts',
                        'Ten of Hearts',
                        'Nine of Hearts',
                        'Eight of Hearts',
                        'Seven of Hearts',
                        'Ace of Hearts',
                        'King of Spades',
                        'Queen of Spades',
                        'Jack of Spades',
                        'Ten of Spades',
                        'Nine of Spades',
                        'Eight of Spades',
                        'Seven of Spades',
                        'Ace of Spades']
        self.assertSequenceEqual([str(card) for card in BeloteDeck()],
                                 belotte_deck)

    def test_sixtysix_deck(self):
        sixtysix_deck = ['King of Diamonds',
                         'Queen of Diamonds',
                         'Jack of Diamonds',
                         'Ten of Diamonds',
                         'Nine of Diamonds',
                         'Ace of Diamonds',
                         'King of Clubs',
                         'Queen of Clubs',
                         'Jack of Clubs',
                         'Ten of Clubs',
                         'Nine of Clubs',
                         'Ace of Clubs',
                         'King of Hearts',
                         'Queen of Hearts',
                         'Jack of Hearts',
                         'Ten of Hearts',
                         'Nine of Hearts',
                         'Ace of Hearts',
                         'King of Spades',
                         'Queen of Spades',
                         'Jack of Spades',
                         'Ten of Spades',
                         'Nine of Spades',
                         'Ace of Spades']
        self.assertSequenceEqual([str(card) for card in SixtySixDeck()],
                                 sixtysix_deck)


if __name__ == '__main__':
    unittest.main()