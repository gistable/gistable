# BITRIS - Copyright 2017 Darryl Sloan

from microbit import *
import neopixel
from random import randint

# Enable NeoPixels to use x & y values
def np_plot(x, y, r, g, b):
    np[31-y-abs(x-3)*8] = (r, g, b)

# Counter explode effect
def counter_explode(x, y):
    for glow in range(30, -1, -1):
        np_plot(x, y, glow, glow, glow)
        np.show()
        sleep(10)

# Game setup
np = neopixel.NeoPixel(pin0, 32)
grid = [randint(1, 6), 0, 0, 0, 0, 0, 0, 0], [randint(1, 6), 0, 0, 0, 0, 0, 0, 0], [randint(1, 6), 0, 0, 0, 0, 0, 0, 0], [randint(1, 6), 0, 0, 0, 0, 0, 0, 0]
col_combo = [[0, 0, 0], [20, 0, 0], [0, 20, 0], [0, 0, 20], [20, 20, 0], [20, 0, 20], [0, 20, 20], [20, 20, 20]]
player_x, player_y, timer, score, instability = 0, 0, 0, 0, 0
alive = True
counter = grid[0][0]

# Main game loop
while alive == True:

    # Display

    # Display grid
    for y in range(0, 8):
        for x in range(0, 4):
            np_plot(x, y, col_combo[grid[x][y]][0], col_combo[grid[x][y]][1], col_combo[grid[x][y]][2])

    # Display player
    np_plot(player_x, player_y, col_combo[counter][0], col_combo[counter][1], col_combo[counter][2])
    np.show()
    
    # Consequences

    # Counter lands on bottom or on another counter
    if player_y == 7 or grid[player_x][player_y+1] > 0:
        grid[player_x][player_y] = counter
        player_y = 0
        player_x = 0
        timer = 0
        counter = grid[0][0]

    # Scan grid for "L" shape
    for y in range(1, 7):
        for x in range(0, 3):
            for colour in range(1, 7):
                square = [[False, False], [False, False]]
                counter_sum = 0
                if grid[x][y] == colour:
                    square[0][0] = True
                    counter_sum += 1
                if grid[x][y+1] == colour:
                    square[0][1] = True
                    counter_sum += 1
                if grid[x+1][y] == colour:
                    square[1][0] = True
                    counter_sum += 1
                if grid[x+1][y+1] == colour:
                    square[1][1] = True
                    counter_sum += 1
                if counter_sum >= 3:
                    for i in [0, 0], [1, 0], [0, 1], [1, 1]:
                        if square[i[0]][i[1]] == True:
                            grid[x+i[0]][y+i[1]] = 0
                            counter_explode(x+i[0],y+i[1])
                    score += 1
                    break

    # Landed white counter explodes and changes counter underneath
    for y in range(1, 8):
        for x in range(0, 4):
            if grid[x][y] == 7:
                grid[x][y] = 0
                counter_explode(x, y)
                if y < 7:
                    for i in range(40):
                         np_plot(x, y+1, randint(0, 20), randint(0, 20), randint(0, 20))
                         np.show()
                         sleep(20)
                    grid[x][y+1] = randint(1, 6)

    # Gravity collapses any gaps between counters
    for y in range(1, 7):
        for x in range(0, 4):
            if grid[x][y] > 0 and grid[x][y+1] == 0:
                grid[x][y+1] = grid[x][y]
                grid[x][y] = 0

    # If grid is filled to capacity, game over
    for i in range(0, 4):
        if grid[i][1] > 0:
            alive = False

    # Movements
    # Player movement
    if button_b.was_pressed() and player_x > 0:
        if grid[player_x-1][player_y+1] == 0:
            player_x -= 1
    if button_a.was_pressed() and player_x < 3:
        if grid[player_x+1][player_y+1] == 0:
            player_x += 1

    # Active counter descends
    timer += 1
    if timer == 3:
        player_y += 1
        if player_y == 1:
            grid[0][0] = 0
        timer = 0

    # Shift waiting counters left
    for i in range(0, 3):
        if grid[i][0] == 0:
            grid[i][0] = grid[i+1][0]
            grid[i+1][0] = 0
    if grid[3][0] == 0:
        grid[3][0] = randint(1, 7)

    # Periodically randomise on-screen counters
    instability += 1
    if instability == 400:
        for i in range(80):
            for y in range(1, 8):
                for x in range(0, 4):
                    if grid[x][y] > 0:
                        grid[x][y] = randint(1, 6)
                        np_plot(x, y, randint(0, 20), randint(0, 20), randint(0, 20))
            np.show()
            sleep(20)
        instability = 0

# Game over
for y in range(0, 8):
    for x in range(0, 4):
        if grid[x][y] > 0:
            counter_explode(x, y)
while True:
    display.scroll(str(score))
