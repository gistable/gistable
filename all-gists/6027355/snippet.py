#!/usr/bin/env python
"""
This is a cute little script for easily running shell commands across many
servers using salt.


Copyright (c) 2013 Steven Arcangeli

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""
import functools
import json
import os
import shlex
import stat
import subprocess
import tempfile
import traceback
from cmd import Cmd
from collections import defaultdict

import salt.client


DOTFILE = '.omnishell'


def _color_wrap(termcode):
    """ Create a color-wrapper function for a specific termcode color """
    return lambda x: "\033[%sm%s\033[0m" % (termcode, x)

# pylint: disable=C0103
red, green, yellow, blue, magenta, cyan, white = map(
    _color_wrap, range(31, 38))
# pylint: enable=C0103


def promptyn(msg, default=None):
    """ Display a blocking prompt until the user confirms """
    while True:
        yes = "Y" if default else "y"
        if default or default is None:
            no = "n"
        else:
            no = "N"
        confirm = raw_input("%s [%s/%s]" % (msg, yes, no))
        confirm = confirm.lower().strip()
        if confirm == "y" or confirm == "yes":
            return True
        elif confirm == "n" or confirm == "no":
            return False
        elif len(confirm) == 0 and default is not None:
            return default


def repl_command(fxn):
    """
    Decorator for :class:`cmd.Cmd` methods

    Parses arguments from the arg string and passes them to the method as *args
    and **kwargs.

    """
    @functools.wraps(fxn)
    def wrapper(self, arglist):
        """Wraps the command method"""
        args = []
        kwargs = {}
        if arglist:
            for arg in shlex.split(arglist):
                if '=' in arg:
                    split = arg.split('=')
                    kwargs[split[0]] = split[1]
                else:
                    args.append(arg)
        return fxn(self, *args, **kwargs)
    return wrapper


class SaltTerm(Cmd):

    """
    Interactive commandline interface

    Attributes
    ----------
    running : bool
        True while session is active, False after quitting
    client : :class:`salt.client.LocalClient`
        Instance of the salt client
    target : str
        The salt target pattern
    expr_form : str
        The salt expr_form
    stashes : dict
        Maps stash name to a dict with a target and expr_form
    confirm_overwrite : bool
        If true, require user input before overwriting an existing stash
    autosave : bool
        If true, automatically save stashes to dotfile

    """
    running = False
    client = None
    target = '*'
    expr_form = 'glob'
    stashes = {}
    confirm_overwrite = True
    autosave = True

    def start(self, conf):
        """ Start running the interactive session (blocking) """
        self.stashes = conf.get('stashes', {})
        self.confirm_overwrite = conf.get('confirm_overwrite', True)
        self.autosave = conf.get('autosave', True)
        self.running = True
        self.client = salt.client.LocalClient()
        self.update_prompt()
        while self.running:
            try:
                self.cmdloop()
            except KeyboardInterrupt:
                print
            except:
                traceback.print_exc()

    def help_help(self):
        """Print the help text for help"""
        print "List commands or print details about a command"

    def do_shell(self, arglist):
        """ Run a shell command """
        process = subprocess.Popen(shlex.split(arglist),
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        output, _ = process.communicate()
        print output

    def update_prompt(self):
        """ Update the command prompt """
        self.prompt = magenta('%s:%s> ' % (self.expr_form, self.target))

    @repl_command
    def do_target(self, target, expr_form='glob'):
        """
        Set a new salt target

        Parameters
        ----------
        target : str
            Salt pattern
        expr_form : str, optional
            The salt method to use for target matching (default 'glob')

        """
        self.target = target
        self.expr_form = expr_form
        self.update_prompt()

    def do_l(self, args):
        """ see 'load' """
        self.onecmd('load %s' % args)

    @repl_command
    def do_load(self, stash):
        """ Load a stashed target """
        if stash not in self.stashes:
            print "Stash '%s' not found!" % stash
            return
        else:
            self.onecmd('target %(target)s %(expr_form)s' %
                        self.stashes[stash])

    def do_s(self, args):
        """ see 'stash' """
        self.onecmd('stash %s' % args)

    @repl_command
    def do_stash(self, name):
        """
        Stash the current salt target to be used again later

        Parameters
        ----------
        name : str
            The unique name to give the stash

        """
        if name in self.stashes and self.confirm_overwrite:
            print "Stash '%s' already exists!" % name
            print "Current stash: %(expr_form)s : %(target)s" % \
                self.stashes[name]
            print "New stash: %s : %s" % (self.expr_form, self.target)
            if not promptyn('Overwrite?', True):
                return

        self.stashes[name] = {'target': self.target,
                              'expr_form': self.expr_form,
                              }
        if self.autosave:
            self.onecmd('save')

    @repl_command
    def do_delete(self, name):
        """
        Delete a stash

        Parameters
        ----------
        name : str

        """
        del self.stashes[name]
        if self.autosave:
            self.onecmd('save')

    @repl_command
    def do_list(self):
        """ List the current stashes """
        for name, data in self.stashes.iteritems():
            print "%s : %s : %s" % (name, data['expr_form'], data['target'])

    @repl_command
    def do_save(self):
        """ Save the current stashes to a dotfile """
        dotfile = os.path.join(os.environ.get('HOME', '.'), DOTFILE)
        current_data = load_dotfile()
        current_data['stashes'] = self.stashes
        with open(dotfile, 'w') as outfile:
            json.dump(current_data, outfile)

    def default(self, command):
        """ Run the command on all minions matching the current target """
        result = self.client.cmd(self.target, 'cmd.run', arg=(command,),
                                 timeout=10, expr_form=self.expr_form)

        # Aggregate responses that are the same
        all_responses = defaultdict(list)
        for minion, response in result.iteritems():
            all_responses[response].append(minion)

        # For any response with multiple minions, sort the minions
        for minions in all_responses.itervalues():
            minions.sort()

        # create pairs of minion(s) strings and responses
        aggregate_responses = []
        for response, minions in all_responses.iteritems():
            aggregate_responses.append((','.join(minions), response))

        # sort the responses by the minion name
        aggregate_responses.sort()

        # here's some magic. We want the nice paging from 'less', so we write
        # the output to a file and use subprocess to run 'less' on the file.
        # But the file might have sensitive data, so open it in 0600 mode.
        _, filename = tempfile.mkstemp()
        mode = stat.S_IRUSR | stat.S_IWUSR
        umask_original = os.umask(0)
        outfile = None
        try:
            outfile = os.fdopen(os.open(filename, os.O_WRONLY | os.O_CREAT,
                                        mode), 'w')
            for minions, response in aggregate_responses:
                outfile.write(green(minions))
                outfile.write('\n')
                outfile.write(green('-' * len(minions)))
                outfile.write('\n')
                outfile.write(response)
                outfile.write('\n')
            outfile.flush()
            subprocess.call(['less', '-FXR', filename])
        finally:
            os.umask(umask_original)
            if outfile is not None:
                outfile.close()
            if os.path.exists(filename):
                os.unlink(filename)

    @repl_command
    def do_EOF(self):  # pylint: disable=C0103
        """ Exit """
        return self.onecmd('exit')

    @repl_command
    def do_exit(self):
        """ Exit """
        self.running = False
        print
        return True

    def emptyline(self):
        pass


def load_dotfile():
    """ Load configuration parameters from the dotfile """
    dotfile = os.path.join(os.environ.get('HOME', '.'), DOTFILE)
    if os.path.exists(dotfile):
        with open(dotfile, 'r') as infile:
            return json.load(infile)
    else:
        return {}

if __name__ == '__main__':
    SaltTerm().start(load_dotfile())
