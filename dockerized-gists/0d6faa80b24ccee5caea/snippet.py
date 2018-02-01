# Put this in ~/.nvim/pythonx/
# requires python, see :he nvim-python
from threading import Thread
from time import sleep, strftime


class EventLoop(Thread):
    def __init__(self, vim):
        super(EventLoop, self).__init__()
        self.vim = vim

    def run(self):
        while True:
            sleep(0.1)
            self.vim.session.post('tick')


class NvimClock(object):
    def __init__(self, vim):
        self.vim = vim
        self.eventLoop = EventLoop(vim)
        self.eventLoop.start()

    def on_tick(self):
        self.vim.command('set statusline=%s' % (strftime("%H:%M:%S"),))