height = 7
width  = 7
board_spaces_occupied = [
    [  1,  0,  1,  1,  1,  0,  0],
    [  1,  1,  0,  1,  1,  0,  1],
    [  1,  1,  1,  1,  0,  0,  1],
    [  1,  0,  1,  0,  1,  1,  1],
    [  1,  0,  0,  1,  1,  1,  1],
    [  0,  0,  1,  0,  0,  1,  1],
    [  0,  1,  1,  0,  1,  1,  1],
]
BLANK = 0

def get_legal_moves_slow(move):
    r, c = move

    directions = [ (-1, -1), (-1, 0), (-1, 1),
                    (0, -1),          (0,  1),
                    (1, -1), (1,  0), (1,  1)]

    fringe = [((r+dr,c+dc), (dr,dc)) for dr, dc in directions
            if move_is_legal(r+dr, c+dc)]

    valid_moves = []
    while fringe:
        move, delta = fringe.pop()

        r, c = move
        dr, dc = delta

        if move_is_legal(r,c):
            new_move = ((r+dr, c+dc), (dr,dc))
            fringe.append(new_move)
            valid_moves.append(move)

    return valid_moves

def move_is_legal(row, col):
    return 0 <= row < height and \
           0 <= col < width and \
           board_spaces_occupied[row][col] == BLANK


STAR_DIRECTIONS = [  (-1, 0), (1,  0), # up down
                     (0, -1), (0,  1), # left right
                     (1, -1), (1,  1), (-1, -1), (-1, 1)] # diagonals


def build_blank_space_dict():
    _blank_space_dict = {}
    for c in range(0, height):
        for r in range(0, width):
            _blank_space_dict[(c, r)] = (board_spaces_occupied[c][r] == BLANK)
    return _blank_space_dict


def move_is_legal_from_dict(move, blank_space_dict):
    return 0 <= move[0] < height and \
           0 <= move[1] < width and \
           blank_space_dict[move]


def calculate_first_move_guess_dict(blank_space_dict):
    _first_move_guess_dict = {}
    for r in range(0, height):
        for c in range(0, width):
            rc_tuple = (r, c)
            _first_move_guess_dict[rc_tuple] = []
            for delta_r, delta_c in STAR_DIRECTIONS:
                valid_guesses = []
                dr = delta_r
                dc = delta_c
                move = (r + dr, c + dc)
                while move_is_legal_from_dict(move, blank_space_dict):
                    valid_guesses.append(move)
                    dr += delta_r
                    dc += delta_c
                    move = (r + dr, c + dc)

                _first_move_guess_dict[rc_tuple].append(valid_guesses)
    return _first_move_guess_dict


def get_legal_moves_fast(move):

    # if blank_space_dict is None:
    blank_space_dict = build_blank_space_dict()

    # if first_move_guess_dict is None:
    first_move_guess_dict = calculate_first_move_guess_dict(blank_space_dict)        

    valid_moves = []
    for direction_list in first_move_guess_dict[move]:
        for move in direction_list:
            if blank_space_dict[move]:
                valid_moves.append(move)
            else:
                break # rest of moves in this direction are invalid

    return valid_moves


def main():
    pos = (3,3)
    print('slow ...')
    print(get_legal_moves_slow(pos))
    
    print('fast ...')
    print(get_legal_moves_fast(pos))


if __name__ == '__main__':
    main()