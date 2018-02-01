from sys import argv
from copy import copy


def read_cards(fn):
    with open(fn) as f:
        cards = [l.strip() for l in f]
    return cards


def backtrack(aligned, id_, side, rot):
    if accept(aligned, id_, side, rot):
        output(aligned, id_, side, rot)
    for id_, side, rot in get_iter(aligned):
        if acceptable(aligned, id_, side, rot):
            aligned_cpy = copy(aligned)
            aligned_cpy.append((id_, side, rot))
            backtrack(aligned_cpy, id_, side, rot)


def output(aligned, id_, side, rot):
    print(aligned)


def get_iter(aligned):
    used = set([i[0] for i in aligned])
    for id_ in range(9):
        if id_ in used:
            continue
        for side in range(2):
            for rot in range(4):
                yield id_, side, rot


def accept(aligned, id_, side, rot):
    if len(aligned) < len(cards):
        return False
    return True


def acceptable(aligned, id_, side, rot):
    if len(aligned) == 0:
        return True
    colors = cards[id_][side*8:side*8+8][rot*2:]
    colors += cards[id_][side*8:side*8+8][:rot*2]
    if not fits_left(aligned, colors):
        return False
    if not fits_top(aligned, colors):
        return False
    return True


def fits_top(aligned, colors):
    if len(aligned) in [0, 1, 2]:  # no top neighbor
        return True
    u_id, u_side, u_rot = aligned[-3]
    right_c = cards[u_id][u_side*8:u_side*8+8][(u_rot*2+4) % 8]
    left_c = cards[u_id][u_side*8:u_side*8+8][(u_rot*2+5) % 8]
    if colors[0] == left_c and colors[1] == right_c:
        return True
    return False


def fits_left(aligned, colors):
    if len(aligned) in [0, 3, 6]:  # no left neighbor
        return True
    l_id, l_side, l_rot = aligned[-1]
    upper_c = cards[l_id][l_side*8:l_side*8+8][(2+2*l_rot) % 8]
    lower_c = cards[l_id][l_side*8:l_side*8+8][(3+2*l_rot) % 8]
    if colors[7] == upper_c and colors[6] == lower_c:
        return True
    return False


cards = read_cards(argv[1])


def main():
    backtrack([], 0, 0, 0)

if __name__ == '__main__':
    main()