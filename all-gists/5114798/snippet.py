#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# If you would like to run it on merlin, please use python2.4 instead.
#
# Author: Izidor Matušov <izidor.matusov@gmail.com>
# Date:   09.02.2013

import os
import re
import sys
from math import pi
from subprocess import Popen, PIPE
from time import time

try:
    import gtk
except ImportError:
    print("PyGTK is available to python2.4 on Merlin, run it like this:\n")
    print("python2.4 %s" % (" ".join(sys.argv)))
    sys.exit(0)
import gobject

BOARD_SIZE = 19
CONNECT_N = 6

class Canvas(gtk.DrawingArea):
    """ Canvas board for Connect-k """

    __gsignals__ = {
        'quit' : (gobject.SIGNAL_RUN_FIRST, None, [bool]),
        'first' : (gobject.SIGNAL_RUN_FIRST, None, [int, int]),
        'stones' : (gobject.SIGNAL_RUN_FIRST, None, [int, int, int, int]),
    }

    def __init__(self, is_first):
        super(Canvas, self).__init__()
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.connect('expose-event', self.on_draw)
        self._click_handler = self.connect('button-press-event', self.on_click)

        # Board
        self.board = [[None for i in range(BOARD_SIZE)] for i in range(BOARD_SIZE)]
        # Which things to highlight?
        self.solution = None
        # Moves to send
        self.stones = []

        # Was the first move already played?
        self.first_move = is_first
        # Player's & enemy's symbol
        if is_first:
            self.player, self.enemy = 0, 1
        else:
            self.player, self.enemy = 1, 0

    def on_draw(self, drawing_area, event):
        """ Draw the canvas:

         * background -- white space
         * highlighted solution
         * grid
         * stones
        """
        alloc = self.get_allocation()
        width, height = alloc[2], alloc[3]
        size_x, size_y = width // BOARD_SIZE, height // BOARD_SIZE

        cr_ctxt = self.window.cairo_create() # pylint: disable-msg=E1101
        cairo = gtk.gdk.CairoContext(cr_ctxt)
        
        # Background
        cairo.set_source_rgb(0.7, 0.7, 0.7)
        cairo.rectangle(0, 0, width, height)
        cairo.fill()

        # Highlight the win
        if self.solution is not None:
            x, y, t = self.solution
            player = self.board[y][x]
            cairo.set_source_rgb(1, 0.8, 1)
            while 0 <= y < BOARD_SIZE and 0 <= x < BOARD_SIZE and self.board[y][x] == player:
                cairo.rectangle(x * size_x, y * size_y,
                    size_x, size_y)

                if t == 'h':
                    x, y = x + 1, y
                elif t == 'v':
                    x, y = x, y + 1
                elif t == 'd1':
                    x, y = x + 1, y + 1
                elif t == 'd2':
                    x, y = x - 1, y + 1

            cairo.fill()

        # Grid
        cairo.set_source_rgb(0, 0, 0)
        cairo.set_line_width(1)

        # Horizontal
        for i in range(BOARD_SIZE):
            y = i * size_y
            cairo.move_to(0, y)
            cairo.line_to(width, y)
        # Vertical
        for i in range(BOARD_SIZE):
            x = i * size_x
            cairo.move_to(x, 0)
            cairo.line_to(x, height)
        cairo.stroke()

        # Points
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                owner = self.board[y][x]
                base_x, base_y = x * size_x, y * size_y

                if owner is None:
                    continue

                if owner == 0:
                    cairo.set_source_rgb(0, 0, 0)
                else:
                    cairo.set_source_rgb(1, 1, 1)

                cairo.set_line_width(2)
                radius = min(size_x, size_y) // 2 - 5
                cairo.arc(base_x + size_x // 2, base_y + size_y // 2, radius, 0, 2 * pi)
                cairo.fill()

        return False

    def on_click(self, widget, event, data=None):
        """ Handle click event """
        alloc = self.get_allocation()
        width, height = alloc[2], alloc[3]
        size_x, size_y = width // BOARD_SIZE, height // BOARD_SIZE

        # if the last row/column is not a square, handle it correctly
        x = min(int(event.x // size_x), BOARD_SIZE - 1) 
        y = min(int(event.y // size_y), BOARD_SIZE - 1) 

        if self.board[y][x] is None:
            self.board[y][x] = self.player 
            # Protocol uses 0-based coords
            self.stones.append(x + 1)
            self.stones.append(y + 1)

            # Check solution only after complete move
            if len(self.stones) >= 4:
                self.solution = self.check_board()
            self.queue_draw()

            if self.first_move and len(self.stones) >= 2:
                self.first_move = False
                self.emit('first', *self.stones)
                self.stones = []
            elif len(self.stones) >= 4:
                # Don't allow further input when one of players won
                if self.solution is not None:
                    self.disconnect(self._click_handler)
                    x, y, _ = self.solution
                    assert self.board[y][x] is not None
                    self.emit('quit', self.player == self.board[y][x])
                    return True

                self.emit('stones', *self.stones)
                self.stones = []
        return True

    def enemy_move(self, moves):
        """ Mark moves of the enemy """
        for x, y in moves:
            assert 1 <= x <= BOARD_SIZE and 1 <= y <= BOARD_SIZE
            # Convert to 0-based coords
            x, y = x - 1, y - 1
            assert self.board[y][x] is None
            self.board[y][x] = self.enemy
        self.solution = self.check_board()
        if self.solution is not None:
            self.disconnect(self._click_handler)
            x, y, _ = self.solution
            assert self.board[y][x] is not None
            self.emit('quit', self.player == self.board[y][x])
        self.queue_draw()

    def check_board(self):
        """ Check board if somebody wins
        
        Return (x, y, type) where type can be:
         * h -- horizontal
         * v -- vertical
         * d1 -- left diagonal
         * d2 -- right diagonal
        """
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                player = self.board[y][x]
                if player is None:
                    continue

                for i in range(1, CONNECT_N):
                    dx = x + i
                    if dx >= BOARD_SIZE:
                        break
                    if self.board[y][dx] != player:
                        break
                else:
                    return (x, y, 'h')

                for i in range(1, CONNECT_N):
                    dy = y + i
                    if dy >= BOARD_SIZE:
                        break
                    if self.board[dy][x] != player:
                        break
                else:
                    return (x, y, 'v')

                for i in range(1, CONNECT_N):
                    dx, dy = x + i, y + i
                    if dx >= BOARD_SIZE or dy >= BOARD_SIZE:
                        break
                    if self.board[dy][dx] != player:
                        break
                else:
                    return (x, y, 'd1')

                for i in range(1, CONNECT_N):
                    dx, dy = x - i, y + i
                    if 0 > dx or dy >= BOARD_SIZE:
                        break
                    if self.board[dy][dx] != player:
                        break
                else:
                    return (x, y, 'd2')


class Prolog(object):
    """ Object for communication with prolog code """

    def __init__(self):
        self.proc = Popen([self._find_binary()], bufsize=1, stdin=PIPE, stdout=PIPE)
        self.last_duration = None
        self._should_quit = False

    def _find_binary(self):
        """ Run make and return executable in format of xlogin00 """
        os.system("make")
        for fpath in os.listdir('.'):
            if os.access(fpath, os.X_OK) and \
                re.match(r'x[a-z]{5}[0-9]{2}', fpath):
                return "./" + fpath

    def _cmd(self, cmd):
        """ Pass a command to prolog binary
        
        Track the time needed to respond.
        """
        print("<-- " + cmd[:-1])
        start = time()
        self.proc.stdin.write(cmd.encode())
        self.proc.stdin.flush()
        out = self.proc.stdout.readline()
        self.last_duration = time() - start
        response = out.decode()
        print("--> " + response[:-1])
        print("")

        # Check if prolog is still alive
        if not self._should_quit and self.proc.poll() is not None:
            sys.stderr.write("Prolog died\n")
            sys.exit(1)

        return response

    def start(self):
        """ Send START command """
        move = self._cmd("START;\n")
        x, y = move.strip(';\n').split(':')[1].split(',')
        return (int(x), int(y))

    def _parse_stones(self, response):
        """ Parse response STONES:x1,y1;x2,y2; """
        raw_moves = response.strip(';\n').split(':')[1].split(';')
        moves = [(int(x) for x in move.split(',')) for move in raw_moves]
        assert len(moves) == 2
        return moves

    def first(self, x, y):
        """ Send FIRST command """
        cmd = "FIRST:%d,%d;\n" % (x, y)
        return self._parse_stones(self._cmd(cmd))

    def stones(self, x1, y1, x2, y2):
        """ Send STONES command """
        cmd = "STONES:%d,%d;%d,%d;\n" % (x1, y1, x2, y2)
        return self._parse_stones(self._cmd(cmd))

    def quit(self):
        """ Send QUIT command """
        self._should_quit = True
        self._cmd("QUIT;\n")
        self.proc.communicate()


class App(object):
    """ Class for connecting Canvas, gtk and prolog """

    def __init__(self, is_first):
        window = gtk.Window()
        window.set_title('FLP :: Connect6')
        window.set_resizable(False)
        window.connect('destroy', gtk.main_quit)

        main_vbox = gtk.VBox()

        self.info = gtk.Label()
        self.info.set_alignment(0, 0.5)
        main_vbox.pack_start(self.info, False, False, 10)

        self.canvas = Canvas(is_first)
        self.canvas.set_size_request(608, 608)
        self.canvas.connect('first', self.on_first)
        self.canvas.connect('stones', self.on_stones)
        self.canvas.connect('quit', self.on_quit)
        main_vbox.pack_start(self.canvas, True, True, 0)

        window.add(main_vbox)
        window.show_all()

        self.prolog = Prolog()
        self.is_first = is_first
        self.winner = None
        if self.is_first:
            self.update_info()
        else:
            self.on_start()
    
    def update_info(self):
        """ Update markup of the info bar """
        if self.winner is None:
            if self.is_first:
                starter = "You have"
            else:
                starter = "Prolog has"

            text = "%s black stones    " % (starter)

            if self.prolog.last_duration is None:
                response = 0
            else:
                response = self.prolog.last_duration

            if response >= 1:
                markup_start, markup_end = "<span foreground='red'>", "</span>"
            else:
                markup_start, markup_end = "",""

            text += "Response time: %s%.3fs%s" % (markup_start,
                response, markup_end)
            self.info.set_markup(text)
        elif self.winner:
            self.info.set_markup("<b>You have won!</b>")
            self.info.set_alignment(0.5, 0.5)
        else:
            self.info.set_markup("<b>Prolog has won!</b>")
            self.info.set_alignment(0.5, 0.5)

    def on_start(self):
        """ Let prolog start """
        move = self.prolog.start()
        self.canvas.enemy_move([move])
        self.update_info()

    def on_first(self, widget, x, y):
        """ The first stone was placed """
        moves = self.prolog.first(x, y)
        self.canvas.enemy_move(moves)
        self.update_info()
        
    def on_stones(self, widget, x1, y1, x2, y2):
        """ Two stones were placed """
        try:
            moves = self.prolog.stones(x1, y1, x2, y2)
            self.canvas.enemy_move(moves)
            self.update_info()
        except Exception:
            sys.stderr.write("Invalid response\n")
            sys.exit(1)

    def on_quit(self, widget, is_winner):
        """ Finish prolog """
        self.winner = is_winner
        self.prolog.quit()
        self.update_info()


if __name__ == "__main__":
    is_first = False
    if len(sys.argv) >= 2:
        if "--help" in sys.argv[1:]:
            print("""Human interface for Connect6
FLP, Logic project
Created by Izidor Matusov <xmatus19@stud.fit.vutbr.cz>

{without arguments}\tyou are the second (white) player
<me|first|start|begin>\tstart as the first (black) player
--help\tprint this help message""")
            sys.exit(0)

        for expr in ["me", "first", "start", "begin"]:
            if expr in sys.argv[1:]:
                is_first = True
                break

    App(is_first)
    gtk.main()

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
