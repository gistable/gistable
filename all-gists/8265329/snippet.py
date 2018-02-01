#!/usr/bin/env python


def world():
    world = [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 1, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 1, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 1, 0, 0, 0, 1],
        [1, 0, 1, 1, 1, 1, 1, 1, 0, 1],
        [1, 0, 1, 0, 0, 0, 0, 1, 0, 1],
        [1, 0, 1, 0, 0, 0, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    ]

    player = {
        'x': 1,
        'y': len(world) - 2
    }

    UP, DOWN, LEFT, RIGHT = 'w', 's', 'a', 'd'
    controls = {
        UP: {'x': 0, 'y': -1},
        DOWN: {'x': 0, 'y': 1},
        LEFT: {'x': -1, 'y': 0},
        RIGHT: {'x': 1, 'y': 0},
    }
    controls_keys = (UP, LEFT, DOWN, RIGHT)

    paint(world, player, controls_keys)

    for key in keypresses(controls_keys):
        v = controls[key]
        if world[player['y'] + v['y']][player['x'] + v['x']] == 0:
            player['x'] += v['x']
            player['y'] += v['y']

        paint(world, player, controls_keys)


import os


def paint(world, player, controls_keys):
    # Clear the screen
    os.system('clear')

    # Draw the world
    for y in range(0, len(world)):
        for x in range(0, len(world[0])):
            if player['x'] == x and player['y'] == y:
                char = '#'
            elif world[y][x] == 1:
                char = '.'
            else:
                char = ' '
            print char,
        print  # line break
    print ", ".join(controls_keys), "to move."
    print "Ctrl+C to quit."


import sys
import tty
import termios


def keypresses(keys):
    keymap = {
        '\x03': KeyboardInterrupt,
        '\x04': EOFError,
    }
    while True:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        try:
            tty.setraw(sys.stdin.fileno())
            key = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        if key in keymap:
            raise keymap[key]
        elif key in keys:
            yield key


if __name__ == '__main__':
    try:
        world()
    except KeyboardInterrupt:
        pass
