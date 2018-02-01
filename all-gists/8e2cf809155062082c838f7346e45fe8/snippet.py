import random
from microbit import *

class board:
    grid = None

    def __init__(self):
        self.grid = [
            [False, False, False, False, False],
            [False, False, False, False, False],
            [False, False, False, False, False],
            [False, False, False, False, False],
            [False, False, False, False, False]]

    def __str__(self):
        return ":".join([''.join(['5' if y else '0' for y in x]) for x in self.grid])

    def advance(self, blocks=0):
        self.grid = [[False, False, False, False, False]] + self.grid[:-1]
        e = list(range(5))
        for b in range(blocks):
            x = random.choice(e)
            e.remove(x)
            self.grid[0][x] = True

    def is_clear(self, x, y):
        return not self.grid[x][y]


class player:
    position = 2
    
    def get_point(self):
        return self.position, 4

    def move_left(self):
        if self.position > 0:
            self.position -= 1

    def move_right(self):
        if self.position < 4:
            self.position += 1


class game:
    frame = 0
    state = 0
    message = "Press any button to play."
    frame_delay = 100
    b = None
    p = None

    def is_colision(self):
        x, y = self.p.get_point()
        return self.b.grid[y][x]

    def update(self):
        self.frame += 1
        if self.state in (0, 2):
            if button_a.was_pressed() or button_b.was_pressed():
                self.state = 1
                self.message = ""
                self.frame = 0
                self.b = board()
                self.p = player()
        elif self.state == 1:
            if button_a.was_pressed():
                self.p.move_left()
            if button_b.was_pressed():
                self.p.move_right()
            if self.frame % 5 == 0:
                self.b.advance(blocks=self.frame % 3)
            if self.is_colision():
                self.message = "CRASH! Press any button to play again."
                self.state = 0

    def render(self):
        if self.state == 0:
            display.scroll(self.message, delay=100, loop=True, wait=False)
            self.state = 2
        elif self.state == 1:
            display.show(Image(str(self.b)))
            x, y = self.p.get_point()
            display.set_pixel(x, y, 9)
        elif self.state == 2:
            # currently showing message (state==0)
            pass
        else:
            self.state = 0
            self.message = "bad state"

    def run(self):
        while True:
            self.update()
            self.render()
            sleep(self.frame_delay)


g = game()
g.run()
