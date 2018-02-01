# Mini-project #4 - "Pong"
#
# 'Introduction to Interactive Programming in Python' Course
# RICE University - coursera.org
# by Joe Warren, John Greiner, Stephen Wong, Scott Rixner

import simplegui
import random
import math


# CLASSES
class Base():
    def __init__(self):
        self.mass = 0.1
        self.color = "white"
        self.size = [1.0, 1.0]
        self.pos = [0, 0]
        self.vel = [0, 0]

    def add_force(self, force):
        for i in range(2):
            self.vel[i] += force[i] / self.mass

    def draw(self, canvas):
        pass  # placeholder, call the draw function here

    def simulate(self):
        for i in range(2):
            self.pos[i] += self.vel[i]

    def bounce(self, coords):
        triggered = False
        new_pos = list(self.pos)
        for i in range(2):
            new_pos[i] = self.pos[i] + self.vel[i]
            conditions = [new_pos[i] - (self.size[i] // 2) < coords[0][i],
                          new_pos[i] + (self.size[i] // 2) > coords[1][i]]
            if any(conditions):
                self.vel[i] *= -1
                triggered = True
        return triggered

    def clamp(self, coords):
        triggered = False
        new_pos = list(self.pos)
        for i in range(2):
            new_pos[i] = self.pos[i] + self.vel[i]
            conditions = [new_pos[i] - (self.size[i] // 2) < coords[0][i],
                          new_pos[i] + (self.size[i] // 2) > coords[1][i]]
            if any(conditions):
                self.vel[i] *= 0
                triggered = True
        return triggered

    def get_speed(self):
        return math.sqrt(math.pow(self.vel[0], 2) + math.pow(self.vel[1], 2))


class Ball(Base):
    super_init = Base.__init__
    def __init__(self):
        self.super_init()
        self.mass = 0.2
        self.radius = 12
        self.size = [self.radius * 2] * 2

    def draw(self, canvas):
        canvas.draw_circle(self.pos, self.size[0] // 2, 1,
                           self.color, self.color)


class Player(Base):
    super_init = Base.__init__
    def __init__(self):
        self.super_init()
        self.size = [8, 80]
        self.score = 0
        self.controls = {chr(simplegui.KEY_MAP["down"]): [0, 1],
                         chr(simplegui.KEY_MAP["up"]): [0, -1]}

    def draw(self, canvas):
        corners = [[-0.5, 0.5], [-0.5, -0.5], [0.5, -0.5], [0.5, 0.5]]
        for i in range(len(corners)):
            for j in range(2):
                corners[i][j] = (corners[i][j] * self.size[j]) + self.pos[j]
        canvas.draw_polygon(corners, 1, self.color, self.color)


# GLOBALS
# canvas stuff
WIDTH = 600
HEIGHT = 400
BG = simplegui.load_image("http://dl.dropboxusercontent.com/u/1076274/interactive_python/pong/background.jpg")
# game elements
ball = Ball()
player1 = Player()
player1.pos = [4, HEIGHT // 2]
player1.controls = {chr(simplegui.KEY_MAP["W"]): [0, -1],
                    chr(simplegui.KEY_MAP["S"]): [0, 1]}
player2 = Player()
player2.pos = [WIDTH - 4, HEIGHT // 2]


# HELPERS
def throw_ball():
    ball.pos = [WIDTH // 2, HEIGHT // 2]
    ball.vel = [0, 0]


# EVENT HANDLERS
def new_game():
    global side
    side = 1
    if not random.randint(0, 1):
        side *= -1
    player1.score = 0
    player2.score = 0
    throw_ball()


def draw(canvas):
    global side
    # DRAW BACKGROUND
    canvas.draw_image(BG, (300, 200), (600, 400), (WIDTH // 2, HEIGHT // 2),
                     (WIDTH, HEIGHT))
    canvas.draw_line([player1.size[0], 0], [player1.size[0], HEIGHT],
                     1, "White")
    canvas.draw_line([WIDTH - player2.size[0], 0],
                     [WIDTH - player2.size[0], HEIGHT], 1, "White")
    canvas.draw_line([WIDTH // 2, 0], [WIDTH // 2, HEIGHT], 1, "White")
    if not ball.get_speed():
        canvas.draw_text("PRESS SPACEBAR TO RESPAWN", (120, HEIGHT // 3),
                         24, "white", "sans-serif")
    # DRAW SCORE
    args = [40, "White", "sans-serif"]
    canvas.draw_text(str(player1.score), (60, 50), *args)
    canvas.draw_text(str(player2.score), (WIDTH - 80, 50), *args)

    # DRAW PADDLES
    for each in (player1, player2):
        each.clamp(((0, 0), (0, HEIGHT)))
        each.simulate()
        each.draw(canvas)

    # DRAW BALL
    if ball.bounce(((player1.size[0], 0), (WIDTH - player2.size[0], HEIGHT))):
        # there's a bounce, who scores?
        if player1.pos[0] + player1.size[0] >= ball.pos[0] - ball.vel[0] - ball.radius:
            if not (player1.pos[1] - player1.size[1] // 2 < ball.pos[1] - ball.vel[0] < player1.pos[1] + player1.size[1] // 2):
                player2.score += 1
                side = 1
                throw_ball()
        elif player2.pos[0] - player2.size[0] <= ball.pos[0] - ball.vel[0] + ball.radius:
            if not (player2.pos[1] - player2.size[1] // 2 < ball.pos[1] - ball.vel[0] < player2.pos[1] + player2.size[1] // 2):
                player1.score += 1
                side = -1
                throw_ball()
    # keep playing
    ball.simulate()
    ball.draw(canvas)
    # increase ball speed as the game goes
    for i in range(2):
        ball.vel[i] *= 1.001


def keydown(key):
    # move paddles
    for each in (player1, player2):
        each.add_force(each.controls.get(chr(key), [0, 0]))
    # throw the ball
    if chr(key) == " ":
        angle = random.random() * 3.142 * 0.333  # [0-60] gradians
        force = [math.abs(math.cos(angle)) * side, -math.abs(math.sin(angle))]
        ball.add_force(force)


def keyup(key):
    for each in (player1, player2):
        if chr(key) in each.controls.keys():
            each.vel = [0, 0]


# create frame
frame = simplegui.create_frame("Pong", WIDTH, HEIGHT)
frame.set_draw_handler(draw)
frame.set_keydown_handler(keydown)
frame.set_keyup_handler(keyup)
frame.add_button("Restart", new_game, 100)

# start frame
frame.start()
new_game()
