import random
import sys


def print_grid(grid):
    print ("\n%s\n" % "+".join([('-' * 4)] * 4)).join(
        ["|".join(["%4d" % item if item > 0 else " " * 4 for item in line]) for line in grid])


def get_available_cells(grid):
    return [(y, x) for y in range(4) for x in range(4) if not grid[y][x]]


def insert_new_item(grid):
    available_cells = get_available_cells(grid)
    if len(available_cells) == 0:
        return False
    y, x = random.choice(available_cells)
    grid[y][x] = 2 if random.random() < 0.9 else 4
    return True


def is_legal_position(y, x):
    return 0 <= y <= 3 and 0 <= x <= 3


def get_next_position(y, x, (y_offset, x_offset)):
    return y + y_offset, x + x_offset


def get_next_nonzero_cell(grid, y, x, (y_offset, x_offset)):
    next_y, next_x = get_next_position(y, x, (y_offset, x_offset))
    if is_legal_position(next_y, next_x):
        if grid[next_y][next_x]:
            return next_y, next_x
        else:
            return get_next_nonzero_cell(grid, next_y, next_x, (y_offset, x_offset))
    else:
        return None, None


def merge_cells(grid, (write_y, write_x), (read_y, read_x), direction, virtual, winning=False):
    if (write_y, write_x) == (read_y, read_x):
        read_y, read_x = get_next_nonzero_cell(grid, read_y, read_x, direction)
    if not is_legal_position(write_y, write_x) or not is_legal_position(read_y, read_x):
        return winning if not virtual else False
    if grid[write_y][write_x]:
        if grid[read_y][read_x] == grid[write_y][write_x]:
            if virtual:
                return True
            grid[write_y][write_x] *= 2
            grid[read_y][read_x] = 0
            return merge_cells(grid, get_next_position(write_y, write_x, direction),
                               get_next_nonzero_cell(grid, read_y, read_x, direction), direction, virtual,
                               winning or grid[write_y][write_x] > 1024)
        else:
            return merge_cells(grid, get_next_position(write_y, write_x, direction),
                               (read_y, read_x), direction, virtual, winning)
    else:
        if virtual:
            return True
        grid[write_y][write_x] = grid[read_y][read_x]
        grid[read_y][read_x] = 0
        return merge_cells(grid, (write_y, write_x),
                           get_next_nonzero_cell(grid, read_y, read_x, direction), direction, virtual, winning)


def get_movable_directions(grid):
    return [direction for direction in ["a", "d", "w", "s"] if move(grid, direction, True)]


def move(grid, direction, virtual):
    if direction == "a":  #left
        return any([merge_cells(grid, (i, 0), (i, 0), (0, 1), virtual) for i in range(4)])
    elif direction == "d":  #right
        return any([merge_cells(grid, (i, 3), (i, 3), (0, -1), virtual) for i in range(4)])
    elif direction == "w":  #up
        return any([merge_cells(grid, (0, i), (0, i), (1, 0), virtual) for i in range(4)])
    elif direction == "s":  #down
        return any([merge_cells(grid, (3, i), (3, i), (-1, 0), virtual) for i in range(4)])


grid = [[0 for x in range(4)] for y in range(4)]
insert_new_item(grid)
while True:
    insert_new_item(grid)
    print_grid(grid)
    movable_directions = get_movable_directions(grid)
    if len(movable_directions) == 0:
        print "You lose!"
        break
    direction_name = sys.stdin.readline().strip().lower()
    while direction_name not in movable_directions:
        print "Invalid direction."
        direction_name = sys.stdin.readline().strip().lower()
    if move(grid, direction_name, False):
        print_grid(grid)
        print "You win!"
        break