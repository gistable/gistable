from __future__ import division
from random import random
import numpy as np
import pandas as pd

'''
    Use regret-matching algorithm to play Scissors-Rock-Paper.
'''

class RPS:
    actions = ['ROCK', 'PAPER', 'SCISSORS']
    n_actions = 3
    utilities = pd.DataFrame([
        # ROCK  PAPER  SCISSORS
        [ 0,    -1,    1], # ROCK
        [ 1,     0,   -1], # PAPER
        [-1,     1,    0]  # SCISSORS
    ], columns=actions, index=actions)


class Player:
    def __init__(self, name):
        self.strategy, self.avg_strategy,\
        self.strategy_sum, self.regret_sum = np.zeros((4, RPS.n_actions))
        self.name = name

    def __repr__(self):
        return self.name

    def update_strategy(self):
        """
        set the preference (strategy) of choosing an action to be proportional to positive regrets
        e.g, a strategy that prefers PAPER can be [0.2, 0.6, 0.2]
        """
        self.strategy = np.copy(self.regret_sum)
        self.strategy[self.strategy < 0] = 0  # reset negative regrets to zero

        summation = sum(self.strategy)
        if summation > 0:
            # normalise
            self.strategy /= summation
        else:
            # uniform distribution to reduce exploitability
            self.strategy = np.repeat(1 / RPS.n_actions, RPS.n_actions)

        self.strategy_sum += self.strategy

    def regret(self, my_action, opp_action):
        """
        we here define the regret of not having chosen an action as the difference between the utility of that action
        and the utility of the action we actually chose, with respect to the fixed choices of the other player.

        compute the regret and add it to regret sum.
        """
        result = RPS.utilities.loc[my_action, opp_action]
        facts = RPS.utilities.loc[:, opp_action].values
        regret = facts - result
        self.regret_sum += regret

    def action(self, use_avg=False):
        """
        select an action according to strategy probabilities
        """
        strategy = self.avg_strategy if use_avg else self.strategy
        return np.random.choice(RPS.actions, p=strategy)

    def learn_avg_strategy(self):
        # averaged strategy converges to Nash Equilibrium
        summation = sum(self.strategy_sum)
        if summation > 0:
            self.avg_strategy = self.strategy_sum / summation
        else:
            self.avg_strategy = np.repeat(1/RPS.n_actions, RPS.n_actions)


class Game:
    def __init__(self, max_game=10000):
        self.p1 = Player('Alasdair')
        self.p2 = Player('Calum')
        self.max_game = max_game

    def winner(self, a1, a2):
        result = RPS.utilities.loc[a1, a2]
        if result == 1:     return self.p1
        elif result == -1:  return self.p2
        else:               return 'Draw'

    def play(self, avg_regret_matching=False):
        def play_regret_matching():
            for i in xrange(0, self.max_game):
                self.p1.update_strategy()
                self.p2.update_strategy()
                a1 = self.p1.action()
                a2 = self.p2.action()
                self.p1.regret(a1, a2)
                self.p2.regret(a2, a1)

                winner = self.winner(a1, a2)
                num_wins[winner] += 1

        def play_avg_regret_matching():
            for i in xrange(0, self.max_game):
                a1 = self.p1.action(use_avg=True)
                a2 = self.p2.action(use_avg=True)
                winner = self.winner(a1, a2)
                num_wins[winner] += 1

        num_wins = {
            self.p1: 0,
            self.p2: 0,
            'Draw': 0
        }

        play_regret_matching() if not avg_regret_matching else play_avg_regret_matching()
        print num_wins

    def conclude(self):
        """
        let two players conclude the average strategy from the previous strategy stats 
        """
        self.p1.learn_avg_strategy()
        self.p2.learn_avg_strategy()


if __name__ == '__main__':
    game = Game()

    print '==== Use simple regret-matching strategy === '
    game.play()
    print '==== Use averaged regret-matching strategy === '
    game.conclude()
    game.play(avg_regret_matching=True)