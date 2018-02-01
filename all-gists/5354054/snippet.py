#!/usr/bin/env python

import os
import cmd


def file_auto_complete(text, line, begidx, endidx):
    """ auto complete of file name.
    """
    line = line.split()
    if len(line) < 2:
        filename = ''
        path = './'
    else:
        path = line[-1]
        if '/' in path:
            i = path.rfind('/')
            filename = path[i+1:]
            path = path[:i]
        else:
            filename = path
            path = './'

    annotate = lambda x : x+'/' if os.path.isdir(os.path.join(path, x)) else x
    ls = map(annotate, sorted(os.listdir(path)))
    if filename == '':
        return ls
    else:
        return [f for f in ls if f.startswith(filename)]


def auto_complete(func):
    """ auto_complete decorator.
    func is not changed, only add 'complete_' method.
    """
    def _complete(self, *args):
        return file_auto_complete(*args)
    # Add 'complete_' method to super class.
    setattr(cmd.Cmd, 'complete_' + func.__name__[3:], _complete)
    return func


class MyCmd(cmd.Cmd):
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = '(MyCmd)'

    @auto_complete
    def do_foo(self, line):
        print('foo ' + line)

    @auto_complete
    def do_bar(self, line):
        print('bar' + line)


if __name__ == '__main__':
    mycmd = MyCmd()
    mycmd.cmdloop()
