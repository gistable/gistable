# A trivial code for solving the Colossal Cue Adventure
# URL: http://adventure.cueup.com/

# Level 1: The VAX's MTH$RANDOM % 36 Roulette

def vax_rng_next(x):
    """Generate the next pseudo-random number."""
    a, c, m = 69069, 1, 2**32
    return (a * x + c) % m

def bet_strategy(n, seed = 6):
    """Calculate the numbers that the ball lands on."""
    x = seed
    print 'initial seed =', x
    for i in range(n):
        x = vax_rng_next(x)
        print '-' * 10
        print 'vax random number =', x
        print 'bet on', x % 36

# Level 2: The Index of The Incorrect Closing Mark
# src_text = '{{[{{{{}}{{}}}[]}[][{}][({[(({{[][()()]}}{[{{{}}}]}))][()]{[[{((()))({}(())[][])}][]()]}{()[()]}]})][]]}{{}[]}}'

def incorrect_at(src_text):
    """Find the index of the incorrect closing mark."""
    mark_pairs = {
        '{': '}',
        '[': ']',
        '(': ')'
    }
    stack = []
    for index, mark in enumerate(src_text):
        if mark in mark_pairs.keys():
            stack.append(mark)
        else:
            opening_mark = stack.pop()
            if mark != mark_pairs[opening_mark]:
                return index, mark
    print 'No incorrect closing mark exists'

# Level 3: The Cartoon Maze
# maze = [[8, 8, 4, 4, 5],
#         [4, 9, 6, 4, 8],
#         [8, 6, 4, 1, 2],
#         [4, 8, 2, 6, 3],
#         [0, 6, 8, 8, 4]]

def find_path(maze, ini_pos = (0, 4), goal = (4, 0), chips = 35, extra_fee = 0):
    """Find the exact-costing path to the goal."""

    def rec(maze, pos, path, chips):

        def on_map(pos):
            x, y = pos
            return 0 <= y < len(maze) and 0 <= x < len(maze[y])

        def enough_chips(pos):
            x, y = pos
            return maze[y][x] <= chips

        # for level 5
        def copy_maze(maze):
            new_maze = []
            for row in maze:
                new_maze.append(row[:])
            return new_maze

        # for level 5
        def raise_fee(maze):
            for y in range(len(maze)):
                for x in range(len(maze[y])):
                    if (x, y) != ini_pos and (x, y) != goal:
                        maze[y][x] += extra_fee
            return maze

        if pos == goal:
            if chips == 0:
                return path + [goal]
            else:
                return False
        else:
            x, y = pos
            candidates = [(x, y - 1), (x + 1, y), (x, y + 1), (x - 1, y)]
            candidates = filter(on_map, candidates)
            candidates = filter(enough_chips, candidates)
            for next_pos in candidates:
                cost = maze[next_pos[1]][next_pos[0]]
                new_maze = raise_fee(copy_maze(maze))
                found_path = rec(new_maze, next_pos, path + [pos], chips - cost)
                if found_path:
                    return found_path
            return False

    return rec(maze, ini_pos, [], chips)

def make_guide(path):
    """Make a guide from a path."""

    if len(path) == 0:
        return False

    guide = []
    ref = path[0]
    for pos in path[1:]:
        dx, dy = pos[0] - ref[0], pos[1] - ref[1]
        if (dx, dy) == (0, -1):
            guide.append('north')
        elif (dx, dy) == (1, 0):
            guide.append('east')
        elif (dx, dy) == (0, 1):
            guide.append('south')
        elif (dx, dy) == (-1, 0):
            guide.append('west')
        else:
            print 'invalid move: (dx, dy) =', (dx, dy)
            return False
        ref = pos
    return guide

# Level 4: The VAX's MTH$RANDOM % 36 Roulette Again
# seq = [34, 27, 16, 1, 34, 31, 24, 17, 34, 35, 16, 13]

def vax_rng(seed = 6):
    """Generate pseudo-random numbers."""
    x = seed
    while True:
        x = vax_rng_next(x)
        yield x % 36

def find_seq(seq, show_next = 5):
    """Find numbers following the given pseudo-random numbers."""
    i = 0
    for j, x in enumerate(vax_rng()):
        if j > 2**32:
            return False
        if i >= len(seq):
            if show_next > 0:
                print x
                show_next -= 1
                continue
            else:
                return True
        if seq[i] == x:
            i += 1
        else:
            i = 0

# Level 5: The Cartoon Maze Again
# maze = [[0, 8, 1, 7, 8, 8, 5, 2, 9, 5, 9, 5],
#         [8, 5, 1, 1, 5, 6, 9, 4, 4, 5, 2, 1],
#         [7, 2, 3, 5, 2, 9, 2, 6, 9, 3, 9, 4],
#         [9, 2, 5, 9, 8, 9, 5, 7, 7, 5, 9, 6],
#         [2, 4, 6, 7, 1, 4, 2, 6, 6, 2, 5, 8],
#         [2, 8, 1, 5, 3, 8, 4, 9, 7, 5, 2, 3],
#         [2, 9, 3, 5, 6, 7, 2, 4, 9, 4, 2, 5],
#         [6, 3, 1, 7, 8, 2, 3, 3, 6, 7, 9, 3],
#         [2, 5, 7, 4, 2, 7, 8, 5, 5, 3, 5, 8],
#         [5, 2, 9, 8, 3, 6, 1, 4, 9, 5, 6, 3],
#         [4, 6, 9, 8, 5, 4, 9, 7, 6, 4, 6, 8],
#         [2, 7, 7, 1, 9, 9, 7, 3, 7, 2, 2, 5]]
# try this:
#     make_guide(find_path(maze, (0, 0), (11, 11), 444, 1))
