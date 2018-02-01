import math
import random

def get_random_neighbour(state):
    neighbour = [house[:] for house in state] # Deep copy

    i, j = random.sample(xrange(5), 2)
    attr_idx = random.randint(0, 4)

    neighbour[i][attr_idx], neighbour[j][attr_idx] = neighbour[j][attr_idx], neighbour[i][attr_idx]
    return neighbour

NAT = 0
COL = 1
ANI = 2
BEV = 3
CIG = 4

def cost_of_state(state):
    cost = 15
    for i, h in enumerate(state):
        cost -= sum([
            h[NAT] == 'brit' and h[COL] == 'red',
            h[NAT] == 'swede' and h[ANI] == 'dog',
            h[NAT] == 'dane' and h[BEV] == 'tea',
            i < 4 and h[COL] == 'green' and state[i+1][COL] == 'white',
            h[COL] == 'green' and h[BEV] == 'coffee',
            h[CIG] == 'pall mall' and h[ANI] == 'bird',
            h[COL] == 'yellow' and h[CIG] == 'dunhill',
            i == 2 and h[BEV] == 'milk',
            i == 0 and h[NAT] == 'norwegian',
            h[CIG] == 'blends' and ((i > 0 and state[i-1][ANI] == 'cat') or (i < 4 and state[i+1][ANI] == 'cat')),
            h[ANI] == 'horse' and ((i > 0 and state[i-1][CIG] == 'dunhill') or (i < 4 and state[i+1][CIG] == 'dunhill')),
            h[CIG] == 'blue master' and h[BEV] == 'root beer',
            h[NAT] == 'german' and h[CIG] == 'prince',
            h[NAT] == 'norwegian' and ((i > 0 and state[i-1][COL] == 'blue') or (i < 4 and state[i+1][COL] == 'blue')),
            h[CIG] == 'blends' and ((i > 0 and state[i-1][BEV] == 'water') or (i < 4 and state[i+1][BEV] == 'water')),
        ])
    return cost

def sa(initial):
    current = initial
    current_cost = cost_of_state(current)
    temp = 1.0
    num_iterations = 0

    while current_cost > 0:
        neighbour = get_random_neighbour(current)
        neighbour_cost = cost_of_state(neighbour)

        cost_delta = neighbour_cost - current_cost

        if cost_delta <= 0 or random.random() < math.exp(-cost_delta/temp):
            current, current_cost = neighbour, neighbour_cost

        num_iterations += 1
        if num_iterations % 500 == 0 and temp > 0.20:
            temp -= 0.05

    return current, num_iterations

def main():
    nationalities = [ 'dane',      'brit',   'swede',       'norwegian', 'german'    ]
    colours       = [ 'yellow',    'red',    'white',       'green',     'blue'      ]
    animals       = [ 'horse',     'cat',    'bird',        'fish',      'dog'       ]
    beverages     = [ 'water',     'tea',    'milk',        'coffee',    'root beer' ]
    cigars        = [ 'pall mall', 'prince', 'blue master', 'dunhill',   'blends'    ]

    attributes = [nationalities, colours, animals, beverages, cigars]

    NUM_HOUSES = 5
    initial = []

    for i in xrange(NUM_HOUSES):
        initial.append([attr[i] for attr in attributes])

    random.seed(100)

    solution, iterations = sa(initial)

    for house in solution:
        print house

    print 'Number of iterations:', iterations

if __name__ == "__main__":
    main()
