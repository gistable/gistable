#!/usr/bin/python
# -*- coding: latin-1 -*-

import urwid
import json
import subprocess

class TaskWarrior(object):

    def pending_tasks(self):
        raw_output = subprocess.check_output(['task', 'export',
            'status:pending'])

        task_json = '[%s]' % raw_output
        return json.loads(task_json, strict=False)

    def complete(self, task):
        subprocess.call(['task', task['uuid'], 'done'])

    def delete(self, task):
        subprocess.call(['task', task['uuid'], 'rc.confirmation:no', 'del'])

    def add(self, value):
        subprocess.call(['task', 'add', value])

    def mod(self, task, value):
        subprocess.call(['task', task['uuid'], 'mod', value])

    def undo(self):
        subprocess.call(['task', 'rc.confirmation:no', 'undo'])


class TaskWidget (urwid.WidgetWrap):

    def __init__ (self, task):
        self.task = task

        desc = urwid.Text(task.get('description', ''))
        proj = urwid.Text(task.get('project','') + ' ', align='right')

        due = urwid.Text(task.get('due',''), align='right')

        item = urwid.AttrMap(urwid.Columns([
            ('fixed', 11, urwid.AttrWrap(proj, 'proj', 'proj_focus')),
            desc,
            due
        ]), 'body', 'body_focus')

        urwid.WidgetWrap.__init__(self, item)

    def selectable (self):
        return True

    def keypress(self, size, key):
        return key


class LineEditor(urwid.Edit):

    __metaclass__ = urwid.signals.MetaSignals
    signals = ['done']

    def keypress(self, size, key):
        if key == 'enter':
            urwid.emit_signal(self, 'done', self.get_edit_text())
            return

        if key == 'esc':
            urwid.emit_signal(self, 'done', None)
            return

        return urwid.Edit.keypress(self, size, key)


class ScrollingListBox(urwid.ListBox):

    def scroll_down(self):
        self.set_focus(self.get_focus()[1] + 1)

    def scroll_up(self):
        focus = self.get_focus()[1]
        if focus > 0:
            self.set_focus(focus - 1)

    def mouse_event(self, size, event, button, col, row, focus):
        button_map = {
            4: self.scroll_down,
            5: self.scroll_up
        }

        if button in button_map:
            button_map[button]()

        return urwid.ListBox.mouse_event(self, size, event, button, col, row, focus)

    def keypress(self, size, key):
        key_map = {
            'j': self.scroll_down,
            'k': self.scroll_up
        }

        if key in key_map:
            key_map[key]()

        return urwid.ListBox.keypress(self, size, key)



class Tasky(object):

    palette = [
        ('proj', '', '', '', 'dark green', ''),
        ('proj_focus', '', '', '', 'dark gray', 'dark green'),
        ('body','', '', '', 'dark blue', ''),
        ('body_focus', '', '', '', 'dark gray', 'dark cyan'),
        ('head','light red', 'black'),
    ]

    def __init__(self):

        self.warrior = TaskWarrior()

        header = urwid.AttrMap(urwid.Text('tasky.α'), 'head')
        self.walker = urwid.SimpleListWalker([])
        self.list_box = ScrollingListBox(self.walker)
        self.view = urwid.Frame(urwid.AttrWrap(self.list_box, 'body'), header=header)
        self.refresh()

        loop = urwid.MainLoop(self.view, Tasky.palette, unhandled_input=self.keystroke)
        loop.screen.set_terminal_properties(colors=256)
        loop.run()

    def refresh(self):
        self.walker[:] = map(TaskWidget, self.warrior.pending_tasks())

    def keystroke(self, input):
        def exit():
            raise urwid.ExitMainLoop()

        def undo():
            self.warrior.undo()
            self.refresh()

        view_action_map = {
            'q': exit,
            'Q': exit,
            'r': self.refresh,
            'u': undo,
            'i': self.new_task,
            ':': self.command_mode,
            '!': self.shell_mode
        }

        task_action_map = {
            'enter': (self.edit_task, False),
            'e': (self.edit_task, False),
            'n': (self.task_note, False),
            'c': (self.warrior.complete, True),
            'd': (self.warrior.delete, True),
        }

        if input in view_action_map:
            view_action_map[input]()

        if input in task_action_map:
            (action, should_refresh) = task_action_map[input]
            action(self.selected_task())
            if should_refresh:
                self.refresh()

    def selected_task(self):
        return self.list_box.get_focus()[0].task


    def task_note(self, task):
        subprocess.call("tmux split-window 'tasknote %i'" % task['id'], shell=True)

    def present_editor(self, prompt, text, handler):
        self.foot = LineEditor(prompt, text)
        self.view.set_footer(self.foot)
        self.view.set_focus('footer')
        urwid.connect_signal(self.foot, 'done', handler)

    def command_mode(self):
        self.present_editor(': ', '', self.command_done)

    def shell_mode(self):
        self.present_editor('! ', '', self.shell_done)

    def edit_task(self, task):
        self.edited_task = task
        self.present_editor(' >> ', task['description'], self.edit_done)

    def new_task(self):
        self.present_editor(' >> ', '', self.new_done)

    def dismiss_editor(action):
        def wrapped(self, content):
            self.view.set_focus('body')
            urwid.disconnect_signal(self, self.foot, 'done', action)
            if content:
                action(self, content)
            self.view.set_footer(None)

        return wrapped

    @dismiss_editor
    def edit_done(self, content):
        self.warrior.mod(self.edited_task, content)
        self.edited_task = None
        self.refresh()

    @dismiss_editor
    def new_done(self, content):
        self.warrior.add(content)
        self.refresh()

    @dismiss_editor
    def command_done(self, content):
        subprocess.call("task %s" % content)
        self.refresh()

    @dismiss_editor
    def shell_done(self, content):
        subprocess.call("tmux split-window '%s'" % content, shell=True)



if __name__ == '__main__':
    Tasky()
