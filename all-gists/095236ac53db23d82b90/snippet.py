from contextlib import contextmanager

class SwitchError(RuntimeError):
    pass

@contextmanager
def switch(switch_value, *, ignore_nomatch=True):
    blocks = {}
    blocks.default = None

    def case(case_value):
        '''Decorator to mark a particular switch case'''
        def decorator(func):
            if blocks.setdefault(case_value, func) is not func:
                raise SwitchError('Repeated case: {}'.format(case_value))
            return func
        return decorator

    def default(func):
        '''Decorator to mark the default switch case'''
        if blocks.default is not None:
            raise SwitchError('Repeated default case')
        blocks.default = func
        return func

    yield case, default
    
    def default_block():
        if not ignore_nomatch:
            raise SwitchError('No switch block matched')

    blocks.get(switch_value, blocks.default or default_block)()

## EXAMPLE

from enum import Enum

class Suit(Enum):
    hearts = 1
    diamonds = 2
    spades = 3
    clubs = 4

def print_card_suit(card):
    with switch(card.suit) as case, default:
        @case(Suit.hearts)
        def _():
            print("Hearts!")

        @case(Suit.diamonds)
        def _():
            print("Diamonds!")

        @case(Suit.spades)
        def _():
            print("Spades!")

        @case(Suit.clubs)
        def _():
            print("Clubs!")

        @default
        def _():
            print("Invalid card suit!")
