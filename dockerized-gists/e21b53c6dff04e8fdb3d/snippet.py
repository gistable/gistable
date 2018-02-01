#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Refactored by Malcolm Jones to work with GTK+3 PyGobject( aka PyGI ). Mar 2016.

# Demo application showing how once can combine the python
# threading module with GObject signals to make a simple thread
# manager class which can be used to stop horrible blocking GUIs.
#
# (c) 2008, John Stowers <john.stowers@gmail.com>
#
# This program serves as an example, and can be freely used, copied, derived
# and redistributed by anyone. No warranty is implied or given.

import os
import sys
import time

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import GObject
GObject.threads_init()

import threading
import time
import random

import StringIO

import re
import ConfigParser
from signal import signal, SIGWINCH, SIGKILL, SIGTERM

from IPython.core.debugger import Tracer
from IPython.core import ultratb

sys.excepthook = ultratb.FormattedTB(mode='Verbose',
                                     color_scheme='Linux',
                                     call_pdb=True,
                                     ostream=sys.__stdout__)

from colorlog import ColoredFormatter

import logging

from gettext import gettext as _

import traceback
from functools import wraps
import Queue


def setup_logger():
    """Return a logger with a default ColoredFormatter."""
    formatter = ColoredFormatter(
        "(%(threadName)-9s) %(log_color)s%(levelname)-8s%(reset)s %(message_log_color)s%(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red',
        },
        secondary_log_colors={
            'message': {
                'ERROR': 'red',
                'CRITICAL': 'red',
                'DEBUG': 'yellow'
            }
        },
        style='%'
    )

    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    return logger


def trace(func):
    """Tracing wrapper to log when function enter/exit happens.
    :param func: Function to wrap
    :type func: callable
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug('Start {!r}'. format(func.__name__))
        result = func(*args, **kwargs)
        logger.debug('End {!r}'. format(func.__name__))
        return result
    return wrapper


# Create a player
logger = setup_logger()


class _IdleObject(GObject.GObject):
    """
    Override GObject.GObject to always emit signals in the main thread
    by emmitting on an idle handler
    """

    @trace
    def __init__(self):
        GObject.GObject.__init__(self)

    @trace
    def emit(self, *args):
        GObject.idle_add(GObject.GObject.emit, self, *args)


class _FooThread(threading.Thread, _IdleObject):
    """
    Cancellable thread which uses gobject signals to return information
    to the GUI.
    """
    __gsignals__ = {
        "completed": (
            GObject.SignalFlags.RUN_LAST, None, []),
        "progress": (
            GObject.SignalFlags.RUN_LAST, None, [
                GObject.TYPE_FLOAT])  # percent complete
    }

    @trace
    def __init__(self, *args):
        threading.Thread.__init__(self)
        _IdleObject.__init__(self)
        self.cancelled = False
        self.data = args[0]
        self.name = args[1]
        self.setName("%s" % self.name)

    @trace
    def cancel(self):
        """
        Threads in python are not cancellable, so we implement our own
        cancellation logic
        """
        self.cancelled = True

    @trace
    def run(self):
        print "Running %s" % str(self)
        for i in range(self.data):
            if self.cancelled:
                break
            time.sleep(0.1)
            self.emit("progress", i / float(self.data) * 100)
        self.emit("completed")


class FooThreadManager:
    """
    Manages many FooThreads. This involves starting and stopping
    said threads, and respecting a maximum num of concurrent threads limit
    """

    @trace
    def __init__(self, maxConcurrentThreads):
        self.maxConcurrentThreads = maxConcurrentThreads
        # stores all threads, running or stopped
        self.fooThreads = {}
        # the pending thread args are used as an index for the stopped threads
        self.pendingFooThreadArgs = []

    @trace
    def _register_thread_completed(self, thread, *args):
        """
        Decrements the count of concurrent threads and starts any
        pending threads if there is space
        """
        del(self.fooThreads[args])
        running = len(self.fooThreads) - len(self.pendingFooThreadArgs)

        print "%s completed. %s running, %s pending" % (
            thread, running, len(self.pendingFooThreadArgs))

        if running < self.maxConcurrentThreads:
            try:
                args = self.pendingFooThreadArgs.pop()
                print "Starting pending %s" % self.fooThreads[args]
                self.fooThreads[args].start()
            except IndexError:
                pass

    @trace
    def make_thread(self, completedCb, progressCb, userData, *args):
        """
        Makes a thread with args. The thread will be started when there is
        a free slot
        """
        running = len(self.fooThreads) - len(self.pendingFooThreadArgs)

        if args not in self.fooThreads:
            thread = _FooThread(*args)
            # signals run in the order connected. Connect the user completed
            # callback first incase they wish to do something
            # before we delete the thread
            thread.connect("completed", completedCb, userData)
            thread.connect("completed", self._register_thread_completed, *args)
            thread.connect("progress", progressCb, userData)
            # This is why we use args, not kwargs, because args are hashable
            self.fooThreads[args] = thread

            if running < self.maxConcurrentThreads:
                print "Starting %s" % thread
                self.fooThreads[args].start()
            else:
                print "Queing %s" % thread
                self.pendingFooThreadArgs.append(args)

    @trace
    def stop_all_threads(self, block=False):
        """
        Stops all threads. If block is True then actually wait for the thread
        to finish (may block the UI)
        """
        for thread in self.fooThreads.values():
            thread.cancel()
            if block:
                if thread.isAlive():
                    thread.join()


class Demo:

    @trace
    def __init__(self):
        # build the GUI
        win = Gtk.Window()
        win.connect("delete_event", self.quit)
        box = Gtk.VBox(False, 4)
        win.add(box)
        addButton = Gtk.Button("Add Thread")
        addButton.connect("clicked", self.add_thread)
        box.pack_start(addButton, False, False, 0)
        stopButton = Gtk.Button("Stop All Threads")
        stopButton.connect("clicked", self.stop_threads)
        box.pack_start(stopButton, False, False, 0)

        # display threads in a treeview
        self.pendingModel = Gtk.ListStore(
            GObject.TYPE_STRING, GObject.TYPE_INT)
        self.completeModel = Gtk.ListStore(GObject.TYPE_STRING)
        self._make_view(self.pendingModel, "Pending Threads", True, box)
        self._make_view(self.completeModel, "Completed Threads", False, box)

        # THE ACTUAL THREAD BIT
        self.manager = FooThreadManager(3)

        # Start the demo
        win.show_all()
        Gtk.main()

    @trace
    def _make_view(self, model, title, showProgress, vbox):
        view = Gtk.TreeView(model)
        view.append_column(Gtk.TreeViewColumn(
            title, Gtk.CellRendererText(), text=0))
        if showProgress:
            view.append_column(Gtk.TreeViewColumn(
                "Progress", Gtk.CellRendererProgress(), value=1))
        vbox.pack_start(view, True, True, 0)

    @trace
    def quit(self, sender, event):
        self.manager.stop_all_threads(block=True)
        Gtk.main_quit()

    @trace
    def stop_threads(self, *args):
        # THE ACTUAL THREAD BIT
        self.manager.stop_all_threads()

    @trace
    def add_thread(self, sender):
        # make a thread and start it
        data = random.randint(20, 60)
        name = "Thread #%s" % random.randint(0, 1000)
        rowref = self.pendingModel.insert(0, (name, 0))

        # THE ACTUAL THREAD BIT
        self.manager.make_thread(
            self.thread_finished,
            self.thread_progress,
            rowref, data, name)

    @trace
    def thread_finished(self, thread, rowref):
        self.pendingModel.remove(rowref)
        self.completeModel.insert(0, (thread.name,))

    @trace
    def thread_progress(self, thread, progress, rowref):
        self.pendingModel.set_value(rowref, 1, int(progress))

if __name__ == "__main__":
    demo = Demo()
