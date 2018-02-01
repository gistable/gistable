"""Pong.
In Nuke.
"""

import nuke

import time
from random import random
import threading


class Player1Score(Exception):
    pass

class Player2Score(Exception):
    pass

class Ball(object):
    def __init__(self, node):
        self.node = node
        self.vx = 4
        self.vy = 0

        # Number of nudge()'s since last collision.
        # Used to prevent multiple collisions on the same object in
        # quick sucession (which makes the ball get stuck in the object)
        self.steps_since_collision = 0
        self.delay_between_collisions = 5

    # Getter/setter for ball location
    def _setxy(self, v):
        x, y = v
        nuke.executeInMainThread(self.node.setXYpos, (x, y))
        time.sleep(0.001)
    def _getxy(self):
        x = self.node.xpos()
        y = self.node.ypos()
        return x, y
    xy = property(_getxy, _setxy)

    def nudge(self):
        """Moves ball with x/y velocity"""
        x, y = self.xy
        self.xy = (x + self.vx, y + self.vy)
        self.steps_since_collision += 1

    def reset(self, gamebox):
        """Reset ball to centre. Reset velocity"""
        x, y = gamebox.xpos(), gamebox.ypos()
        w, h = gamebox.screenWidth(), gamebox.screenHeight()

        cx = x + (w/2)
        cy = y + (h/2)

        r = 2 - (random() * 4)

        if self.vx > 0:
            self.vx, self.vy = 4, 0
        else:
            self.vx, self.vy = -4, 0

        nuke.executeInMainThread(self.node.setXYpos, (cx, cy))

    def check_paddle(self, paddle):
        """Checks collision with paddles"""
        if self.steps_since_collision < self.delay_between_collisions:
            return

        x, y = self.xy
        cx, cy = paddle.xpos(), paddle.ypos()
        cw, ch = paddle.screenWidth(), paddle.screenHeight()

        if y > cy and y < (cy + ch):
            # In correct y location
            if (x > (cx)) and (x < (cx + cw)):
                self.vx = -self.vx
                # Add randomness to bounce
                self.vy = self.vy + (1.0 - (random() * 2.0))
                self.nudge()
                self.steps_since_collision = 0

    def check_gamebox(self, gamebox):
        """Checks for collisions with the edge of game box, and raises the
        appropriate Player{n}Score exception"""
        if self.steps_since_collision < self.delay_between_collisions:
            return

        sx, sy = gamebox.xpos(), gamebox.ypos()
        w, h = gamebox.screenWidth(), gamebox.screenHeight()
        maxx = sx + w
        maxy = sy + h

        x, y = self.xy

        if x < sx:
            self.vx = -self.vx
            self.nudge()
            self.steps_since_collision = 0
            raise Player1Score()

        elif x > maxx:
            self.vx = -self.vx
            self.nudge()
            self.steps_since_collision = 0
            raise Player2Score()

        elif y < sy:
            self.vy = -self.vy
            self.nudge()
            x, y = self.xy
            self.xy = (x, sy)
            self.steps_since_collision = 0

        elif y > maxy:
            self.vy = -self.vy
            self.nudge()
            x, y = self.xy
            self.xy = (x, maxy)
            self.steps_since_collision = 0


class Game(threading.Thread):
    def __init__(self, gamebox, ball, player1, player2):
        threading.Thread.__init__(self)
        self.gamebox = gamebox
        self.ball = ball
        self.left = player1
        self.right = player2

        self.ball = Ball(self.ball)
        self.stop = False

    def deletenodes(self):
        for x in [self.gamebox, self.left, self.right]:
            nuke.delete(nuke.toNode(x.name()))
        nuke.delete(self.ball.node)


    def gameloop(self):
        self.ball.reset(self.gamebox)
        time.sleep(0.1)

        while not self.stop:
            self.ball.nudge()

            toincrement = None
            try:
                self.ball.check_gamebox(self.gamebox)

            except Player1Score:
                print "Player 1 scored"
                toincrement = self.gamebox['p1_score']

            except Player2Score:
                print "Player 2 scored"
                toincrement = self.gamebox['p2_score']

            if toincrement is not None:
                cur = nuke.executeInMainThreadWithResult(toincrement.value)
                if cur is None:
                    cur = 0
                new = cur + 1
                nuke.executeInMainThreadWithResult(toincrement.setValue, new)
                self.ball.reset(self.gamebox)

            self.ball.check_paddle(paddle = self.left)
            self.ball.check_paddle(paddle = self.right)
            time.sleep(0.01)

    def run(self):
        try:
            self.gameloop()
        except Exception, e:
            # Exception in thread doesn't give a useful traceback
            # to Nuke console, print one.
            import traceback
            traceback.print_exc()
            raise


def _nudgeplayer(node, vertical):
    y = node.ypos()
    node.setYpos(y + vertical)

def nudge_up(left = False, right = False, large = False):
    global pong
    if left:
        node = pong.left
    elif right:
        node = pong.right
    else:
        raise ValueError("left or right must be True")

    _nudgeplayer(node, -40 if large else -20)

def nudge_down(left = False, right = False, large = False):
    global pong
    if left:
        node = pong.left
    elif right:
        node = pong.right
    else:
        raise ValueError("left or right must be True")

    _nudgeplayer(node, 40 if large else 20)


global pong
pong = None

def stop_pong():
    global pong
    if pong is None:
        return
    else:
        print "Stopping pong.."
        pong.stop = True
        pong.join()
        pong.deletenodes()
        pong = None

def start_pong():
    stop_pong()

    # Make game box
    gamebox = nuke.toNode("PONG")

    if gamebox is None:
        gamebox = nuke.nodes.BackdropNode(bdwidth = 1000, bdheight = 500)
        p1s = nuke.Int_Knob('p1_score', 'player 1 score')
        p2s = nuke.Int_Knob('p2_score', 'player 2 score')
        gamebox.addKnob(p1s)
        gamebox.addKnob(p2s)
        gamebox['tile_color'].setValue(1)

    ball = nuke.toNode("ball")
    if ball is None:
        ball = nuke.nodes.Dot()

    # Make paddles
    player1, player2 = nuke.toNode("player1"), nuke.toNode("player2")

    if player1 is None:
        player1 = nuke.nodes.BackdropNode(bdwidth = 40, bdheight = 100, name = "player1")
        player1.setXpos(gamebox.xpos())

    if player2 is None:
        player2 = nuke.nodes.BackdropNode(bdwidth = 40, bdheight = 100, name = "player2")
        player2.setXpos(
            (gamebox.xpos() + (gamebox.screenWidth() - 40)))

    global pong
    pong = Game(
        gamebox = gamebox,
        ball = ball,
        player1 = player1,
        player2 = player2)
    pong.start()


def main():
    mn = nuke.menu("Nodes")
    mp = mn.addMenu("Pong")

    mp.addCommand(
        "start pong",
        lambda: start_pong(),
        "alt+p")
    mp.addCommand("stop pong",
                  lambda: stop_pong(),
                  "alt+q")

    mp.addSeparator()
    mp.addCommand("p1 - up",
                  lambda: nudge_up(left=True),
                  "Up")
    mp.addCommand("p1 - up large",
                  lambda: nudge_up(left=True, large=True),
                  "Shift+Up")

    mp.addCommand("p1 - down",
                  lambda: nudge_down(left=True),
                  "Down")
    mp.addCommand("p1 - down large",
                  lambda: nudge_down(left=True, large=True),
                  "Shift+Down")


    mp.addSeparator()
    mp.addCommand("p2 - up",
                  lambda: nudge_up(right=True),
                  "w")
    mp.addCommand("p2 - up large",
                  lambda: nudge_up(right=True, large=True),
                  "Shift+w")

    mp.addCommand("p2 - down",
                  lambda: nudge_down(right=True),
                  "s")
    mp.addCommand("p2 - down large",
                  lambda: nudge_down(right=True, large=True),
                  "Shift+s")


if __name__ == '__main__':
    main()
