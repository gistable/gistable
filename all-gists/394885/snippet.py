#!/usr/bin/python
"""Yet another curses-based directory tree browser, in Python.

I thought I could use something like this for filename entry, kind of
like the old 4DOS 'select' command --- cd $(cursoutline.py).  So you
navigate and hit Enter, and it exits and spits out the file you're on.

Originally from: http://lists.canonical.org/pipermail/kragen-hacks/2005-December/000424.html
Originally by: Kragen Sitaker

"""
# There are several general approaches to the drawing-an-outline
# problem.  This program supports the following operations:
# - move cursor to previous item (in preorder traversal)
# - move cursor to next item (likewise)
# - hide descendants
# - reveal children
# And because it runs over the filesystem, it must be at least somewhat lazy
# about expanding children.
# And it doesn't really bother to worry about someone else changing the outline
# behind its back.
# So the strategy is to store our current linear position in the
# inorder traversal, and defer operations on the current node until the next
# time we're traversing.


import curses.wrapper, time, random, cgitb, os, sys
cgitb.enable(format="text")
ESC = 27
result = ''
start = '.'

def pad(data, width):
    # XXX this won't work with UTF-8
    return data + ' ' * (width - len(data))

class File:
    def __init__(self, name):
        self.name = name
    def render(self, depth, width):
        return pad('%s%s %s' % (' ' * 4 * depth, self.icon(),
                                os.path.basename(self.name)), width)
    def icon(self): return '   '
    def traverse(self): yield self, 0
    def expand(self): pass
    def collapse(self): pass

class Dir(File):
    def __init__(self, name):
        File.__init__(self, name)
        try: self.kidnames = sorted(os.listdir(name))
        except: self.kidnames = None  # probably permission denied
        self.kids = None
        self.expanded = False
    def children(self):
        if self.kidnames is None: return []
        if self.kids is None:
            self.kids = [factory(os.path.join(self.name, kid))
                         for kid in self.kidnames]
        return self.kids
    def icon(self):
        if self.expanded: return '[-]'
        elif self.kidnames is None: return '[?]'
        elif self.children(): return '[+]'
        else: return '[ ]'
    def expand(self): self.expanded = True
    def collapse(self): self.expanded = False
    def traverse(self):
        yield self, 0
        if not self.expanded: return
        for child in self.children():
            for kid, depth in child.traverse():
                yield kid, depth + 1
    
def factory(name):
    if os.path.isdir(name): return Dir(name)
    else: return File(name)

def main(stdscr):
    cargo_cult_routine(stdscr)
    stdscr.nodelay(0)
    mydir = factory(start)
    mydir.expand()
    curidx = 3
    pending_action = None
    pending_save = False

    while 1:
        stdscr.clear()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
        line = 0
        offset = max(0, curidx - curses.LINES + 3)
        for data, depth in mydir.traverse():
            if line == curidx:
                stdscr.attrset(curses.color_pair(1) | curses.A_BOLD)
                if pending_action:
                    getattr(data, pending_action)()
                    pending_action = None
                elif pending_save:
                    global result
                    result = data.name
                    return
            else:
                stdscr.attrset(curses.color_pair(0))
            if 0 <= line - offset < curses.LINES - 1:
                stdscr.addstr(line - offset, 0,
                              data.render(depth, curses.COLS))
            line += 1
        stdscr.refresh()
        ch = stdscr.getch()
        if ch == curses.KEY_UP: curidx -= 1
        elif ch == curses.KEY_DOWN: curidx += 1
        elif ch == curses.KEY_PPAGE:
            curidx -= curses.LINES
            if curidx < 0: curidx = 0
        elif ch == curses.KEY_NPAGE:
            curidx += curses.LINES
            if curidx >= line: curidx = line - 1
        elif ch == curses.KEY_RIGHT: pending_action = 'expand'
        elif ch == curses.KEY_LEFT: pending_action = 'collapse'
        elif ch == ESC: return
        elif ch == ord('\n'): pending_save = True
        curidx %= line

def cargo_cult_routine(win):
    win.clear()
    win.refresh()
    curses.nl()
    curses.noecho()
    win.timeout(0)

def open_tty():
    saved_stdin = os.dup(0)
    saved_stdout = os.dup(1)
    os.close(0)
    os.close(1)
    stdin = os.open('/dev/tty', os.O_RDONLY)
    stdout = os.open('/dev/tty', os.O_RDWR)
    return saved_stdin, saved_stdout

def restore_stdio((saved_stdin, saved_stdout)):
    os.close(0)
    os.close(1)
    os.dup(saved_stdin)
    os.dup(saved_stdout)

if __name__ == '__main__':
    global start
    if len(sys.argv) > 1:
        start = sys.argv[1]
    saved_fds = open_tty()
    try: curses.wrapper(main)
    finally: restore_stdio(saved_fds)
    print result