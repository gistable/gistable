import pygame
import random
from Queue import Queue, deque
from pygame.color import Color

d = 20
WIDTH = 15
HEIGHT = 10

LEFT, RIGHT, UP, DOWN = -1, 1, -WIDTH, WIDTH
DIRECTION = {-1: 'LEFT', 1: 'RIGHT', -WIDTH: 'UP', WIDTH: 'DOWN'}
MOVES = (LEFT, RIGHT, UP, DOWN)
INF = WIDTH*HEIGHT+1
DFS_FAIL_LIMIT = 10

cherry = None
snake = deque()
dfs_fail_count = 0


def is_move_possible(pos, move):
    if move == LEFT:
        return pos % WIDTH > 0
    elif move == RIGHT:
        return pos % WIDTH < WIDTH-1
    elif move == UP:
        return pos >= WIDTH
    elif move == DOWN:
        return pos < (HEIGHT-1)*WIDTH


def get_best_moves(pos, dist, func):
    possible_moves = [mv for mv in MOVES if pos+mv not in list(snake)[:-1]
                      and is_move_possible(pos, mv)]
    if not possible_moves:
        return []
    ds = [dist[pos+mv] for mv in possible_moves if dist[pos+mv] != INF]
    if not ds:
        return []
    return [mv for mv in possible_moves if dist[pos+mv] == func(ds)]


# BFS (from the target)
# return possible_to_reach_target and distance_marix
def reach(target, snake):
    q = Queue()
    q.put(target)
    found = False
    dist = [INF]*(HEIGHT*WIDTH)
    dist[target] = 0
    while not q.empty():
        pos = q.get()
        for mv in MOVES:
            if is_move_possible(pos, mv):
                new_pos = pos + mv
                if new_pos == snake[0]:
                    found = True
                if new_pos not in snake:
                    if dist[new_pos] == INF:
                        dist[new_pos] = dist[pos]+1
                        q.put(new_pos)
    return found, dist


# DFS all the best ways to reach the cherry
# return (True, next_move) if
# it is possible to reach the snake tail after eaten the cherry
def brave(snake, dist):
    global dfs_fail_count
    if dfs_fail_count > DFS_FAIL_LIMIT:  # blance between speed and distance
        return False, None
    if snake[0] == cherry:
        ok, _ = reach(snake[-1], snake)
        ok = ok and any(snake[0]+mv not in snake for mv in MOVES)
        if not ok:
            dfs_fail_count += 1
        return ok, None

    best_moves = get_best_moves(snake[0], dist, min)
    if not best_moves:
        return False, None
    random.shuffle(best_moves)
    for mv in best_moves:
        snake.appendleft(snake[0]+mv)
        if snake[0] != cherry:
            t = snake.pop()
        ok, _ = brave(snake, dist)
        if snake[0] != cherry:
            snake.append(t)
        snake.popleft()
        if ok:
            return True, mv
    return False, None


# make snake to do the next move and return one of 'FRL'
def next_step():
    global dfs_fail_count
    dfs_fail_count = 0
    ok, dist = reach(cherry, snake)
    if ok:
        ok, mv = brave(snake, dist)
    if not ok:  # try to chase the tail and select the longest path
        _, dist = reach(snake[-1], snake)
        best_moves = get_best_moves(snake[0], dist, max)
        mv = random.choice(best_moves)
    # move the snake
    snake.appendleft(snake[0]+mv)
    if snake[0] != cherry:
        snake.pop()
    return DIRECTION[mv]


def draw(window):
    color = Color('black')
    for j in xrange(WIDTH):
        for i in xrange(HEIGHT):
            pygame.draw.rect(window, color, (j*d, i*d, d, d))
    pygame.draw.rect(window, Color('red'),
                     ((cherry % WIDTH)*d, (cherry / WIDTH)*d, d, d))
    n = len(snake)
    for i, pos in enumerate(snake):
        pygame.draw.rect(window, Color(0, (n-i)*255/n, i*255/n),
                         ((pos % WIDTH)*d, (pos / WIDTH)*d, d, d))


def main():
    global cherry
    pygame.init()
    window = pygame.display.set_mode((d*WIDTH, d*HEIGHT))
    pygame.display.set_caption('snakes')
    cherry = random.randint(0, WIDTH*HEIGHT-1)
    snake.append(random.randint(0, WIDTH*HEIGHT-1))
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
        if cherry is not None:
            next_step()
        if snake[0] == cherry:
            possible_cherry = set(xrange(WIDTH*HEIGHT)) - set(snake)
            if not possible_cherry:
                cherry = None
            else:
                cherry = random.choice(list(possible_cherry))
        if cherry:
            draw(window)
            pygame.display.update()
        clock.tick(50)

main()