# Three people are playing the following betting game.
# Every five minutes, a turn takes place in which a random player rests and the other two bet
# against one another with all of their money.
# The player with the smaller amount of money always wins,
# doubling his money by taking it from the loser.
# For example, if the initial amounts of money are 1, 4, and 6,
# then the result of the first turn can be either
# 2,3,6 (1 wins against 4);
# 1,8,2 (4 wins against 6); or
# 2,4,5 (1 wins against 6).
# If two players with the same amount of money play against one another,
# the game immediately ends for all three players.
# Find initial amounts of money for the three players, where none of the three has more than 255,
# and in such a way that the game cannot end in less than one hour. (So at least 12 turns)
# In the example above (1,4,6), there is no way to end the game in less than 15 minutes.
# All numbers must be positive integers.

DESIRED_TURNS = 11
MAX_MONEY = 256


# Calculate all the possible sequences for who misses out for each turn
def calc_events(current=[], turn=0):
    if turn == DESIRED_TURNS:
        return [current]

    one = list(current)
    one.append(0)

    two = list(current)
    two.append(1)

    three = list(current)
    three.append(2)

    turn += 1
    path1 = calc_events(current=one, turn=turn)
    path2 = calc_events(current=two, turn=turn)
    path3 = calc_events(current=three, turn=turn)

    return path1 + path2 + path3


def play_games(p1, p2, p3, events):
    for event in events:

        c1 = p1
        c2 = p2
        c3 = p3

        for x in event:
            if x == 0:
                if c2 == c3:
                    return [False, p1, p2, p3]
                if c2 > c3:
                    c2 = c2 - c3
                    c3 = c3 + c3
                else:
                    c3 = c3 - c2
                    c2 = c2 + c2
            if x == 1:
                if c1 == c3:
                    return [False, p1, p2, p3]
                if c1 > c3:
                    c1 = c1 - c3
                    c3 = c3 + c3
                else:
                    c3 = c3 - c1
                    c1 = c1 + c1
            if x == 2:
                if c1 == c2:
                    return [False, p1, p2, p3]
                if c1 > c2:
                    c1 = c1 - c2
                    c2 = c2 + c2
                else:
                    c2 = c2 - c1
                    c1 = c1 + c1

    return [True, p1, p2, p3]


if __name__ == '__main__':
    possible_events = calc_events()
    combinations = []

    for x in xrange(1, MAX_MONEY):
        for y in xrange(x, MAX_MONEY):
            for z in [b for b in xrange(y, MAX_MONEY) if b != x and b != y]:
                combinations.append([x, y, z])

    results = [play_games(x[0], x[1], x[2], possible_events) for x in combinations]
    print [x for x in results if x[0]]
