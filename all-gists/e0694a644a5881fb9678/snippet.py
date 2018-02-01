__author__ = 'Zeirison'
__version__ = '0.1'

import random

# enemy = int(input("Your opponent (1 - Human, 2 - Computer):"))
# size = int(input("Field size (1 - 3x3, 2 - 4x4, 3 - 5x5, 4 - 6x6:"))
enemy = 1
tic = 1
size = 1
level = 1
# if enemy == 2:
# level = int(input("Game complexity (1 - Easy, 2 - Hard):"))

field = [[2, 0, 2],
         [0, 0, 0],
         [2, 0, 2]]
# field = [[1, 2, 3],
# [4, 5, 6],
# [7, 8, 9]]
# field = [[2, 0, 0, 2],
#          [2, 0, 0, 0],
#          [2, 0, 2, 0],
#          [0, 0, 0, 0]]
# field = []


def field_create():
    for i in range(size + 2):
        field.append([])
        for j in range(size + 2):
            field[i].append(0)


def view_field(a, b, c, d):
    view = ""
    for i in range(size + 2):
        view += "|"
        for j in range(size + 2):
            if field[i][j] == 0:
                view += "_|"
            elif field[i][j] == 1:
                view += "X|"
            elif field[i][j] == 2:
                view += "O|"
        if i == 0:
            view += " --> Status: " + a
        if i == 1:
            view += " --> Opponent: " + b
            if enemy == 2:
                if level == 1:
                    view += " (Easy)"
                elif level == 2:
                    view += " (Hard)"
        if i == 2:
            if not d:
                view += " --> To put '" + c + "' in a section: "
            if d:
                view += " --> Tic-tac-toe " + __version__ + " (by " + __author__ + " )"
        view += "\n"

    print(view)


def drive(a, b):
    i = 0
    j = 0
    tick = 0
    for k in range(size + 2 ** 2):
        if tick == a:
            field[i][j] = b
            break
        elif j == size + 1:
            i += 1
            j = 0
        else:
            j += 1
            tick += 1
    print("i: {0}, j: {1}, tick: {2}".format(i, j, tick))

# print("i: {0}, j: {1}".format(a, b))
# 09.04.15 17:11 - 28
# 09.04.15 17:23 - 2

drive(5, 1)
view_field("Draw!", "Human", "X", False)


def section_check(a, b):
    return field[a][b] == 0


def win_check(a):
    global win, count
    win = 0
    count = 0

    for i in range(size + 2):
        count = 0

        # Проверка по горизонтали
        for j in range(size + 2):
            if field[i][j] == a:
                count += 1
            elif field[j][i] == a:
                count += 1
            elif field[j][j] == a:
                count += 1
            elif field[size + 1 - j][j] == a:
                count += 1
            else:
                count = 0
                break

        if count == 3:
            return 1
        if count == 3:
            break

    return 0


def status_check(a, b=""):
    return {
        0: "Game proceeds.",
        1: "The player '" + b + "' won!",
        2: "The " + b + " won!",
        3: "Draw!"
    }.get(a)


def computer(a):
    slot = []
    for i in range(size + 2):
        for j in range(size + 2):
            if field[i][j] == 0:
                slot.append([i, j])
    random.shuffle(slot)
    field[slot[0][0]][slot[0][1]] = a


# field_create()
# view_field("Draw!", "Human", "X", False)
# computer(2)
view_field("Draw!", "Human", "X", False)
input()


def game():
    global status

    hod = 0
    status = status_check(0)

    if enemy == 1:
        opp = "Human"
    else:
        opp = "Computer"

    field_create()

    if enemy == 1:
        col = 9
    else:
        col = 5

    for i in range(col):

        if hod == 0:
            zn = 1
            mod = 1
            hod = 1
        else:
            zn = 2
            mod = 2
            hod = 0

        # view_field("Draw!", "Human", "X", False)
        view_field(status, opp, zn, False)

        check = False
        while not check:
            num = int(input())
            num -= 1
            check = section_check(num)
            if not check:
                print("This section is already occupied!")

        if enemy == 1:
            field[num] = mod
        else:
            field[num] = mod
            print(i)
            if i != 4:
                if level == 1:
                    field[computer()] = 2
                else:
                    field[computer2()] = 2
            hod = 0

        if enemy == 2:
            if win_check(mod) == 1:
                field[10] = status_check(2, "Human")
            elif win_check(2) == 1:
                field[10] = status_check(2, "Computer")
            elif i == 4:
                field[10] = status_check(3, zn)
                view_field()
        elif enemy == 1:
            if win_check(mod) == 1:
                field[10] = status_check(win_check(mod), zn)
            elif i == 8:
                field[10] = status_check(3, zn)

        if win_check(mod) == 1 or win_check(2) == 1:
            field[12] = " --> Tic-tac-toe v" + __version__
            view_field()
            break


# game()
