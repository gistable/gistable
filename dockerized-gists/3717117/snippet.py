#!/usr/bin/env python

'''
Based on http://ginstrom.com/scribbles/2012/05/10/continuous-integration-in-python-using-watchdog/

Dependencies: ``watchdog`` (pip install watchdog)

Montiors the whole tree for changes.
Check for all changes to any files and test the associated package; we might want to test changes to a pyramid test.ini, say, or a file rename as part of a refactor.

* runs the tests for the package where a change happened first. On failure,
  stops and displays the results.
* should a change happen and the directory it happened to pass, run all of the
  tests
* keep a cache of when a given test was run and don't re-run
'''

import os
import sys
import time
import glob
import signal
import Queue
from subprocess import Popen, PIPE, STDOUT

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


def signal_handler(signal, frame):
    """ Bail out at the top level, our code can get stuck in lots of odd keyboard lands """
    sys.exit(0)


class ChangeHandler(FileSystemEventHandler):
    '''
    React to changes by running tests
    '''

    def __init__(self, runtime):
        self.runtime = runtime

    def on_any_event(self, event):
        self.runtime.run_tests(event.src_path)


class MultiProjectWatch(object):

    def __init__(self):
        self.basedir = os.path.abspath(__file__ + '/../..')
        self.test_ttl = {}
        self.no_rerun_seconds = 2
        self.change_handler = ChangeHandler(self)
        self.observer = Observer()
        self.observer.schedule(
            self.change_handler, self.basedir, recursive=True)
        print "watching for changes in the %s tree" % self.basedir
        self.observer.start()

    def run(self):
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()

    def run_tests(self, modified_path=None):
        '''
        Run unit tests with nosetest.
        If provided, test the immediate module first, then test all the other modules.
        Stop testing if any test fails.
        '''
        # first make sure it's not a vim save file
        if os.path.basename(modified_path).startswith('.'):
            return
        if modified_path is not None:
            modified_pkg = self.find_package(modified_path)
            if modified_pkg is None:
                """ this file wasn't part of a package """
                return
            rv = self.test_package(modified_pkg)
            if not rv:
                return
        for pkg in self.all_packages():
            if pkg != modified_pkg:
                # don't re-test the first package, we already done tested that
                rv = self.test_package(pkg)
                if not rv:
                    return

    def test_package(self, pkg_path):
        """ test a single package. Return True on pass, False on fail """
        now = time.time()
        if (abs(self.test_ttl.get(pkg_path, 0) - now) < self.no_rerun_seconds):
            return
        print "TESTING: %s...." % pkg_path,
        sys.stdout.flush()

        cwd = os.getcwd()
        os.chdir(pkg_path)
        p = Popen('nosetests', shell=True, stdout=PIPE, stdin=None,
                  stderr=STDOUT, close_fds=True)
        rv = p.wait()
        output = p.stdout.read()

        self.test_ttl[pkg_path] = time.time()
        queue = self.observer.event_queue
        try:
            """ dirty hack to drain any events that this test generated """
            while 1:
                queue.get_nowait()
                queue.task_done()
        except Queue.Empty:
            """ this is ok, it's what we expect """
            pass

        os.chdir(cwd)
        if rv == 1:
            print "FAILED"
            print output
            return False
        else:
            print "OK"
            return True

    def find_package(self, path):
        """ Given a path to a file, return the path to the package which contains it.
            This is done by checking for setup.py in each directory from the provided package up.
        """
        directory = path
        while True:
            if os.path.exists(directory + '/setup.py'):
                return os.path.abspath(directory)
            else:
                directory = os.path.dirname(directory)  # cd ..
                if directory == '' or directory == self.basedir:
                    return None

    def all_packages(self):
        """ Return list of paths to all packages rooted under 'self.basedir' """
        os.chdir(self.basedir)
        packages = []
        for setup in glob.glob('./*/setup.py'):
            packages.append(os.path.abspath(setup + '/..'))
        return packages


def main():
    """ main() function when run from the command line.
        runs all the tests to start with, then starts observing from there.
    """
    signal.signal(signal.SIGINT, signal_handler)
    while 1:
        watcher = MultiProjectWatch()
        watcher.run()

if __name__ == '__main__':
    main()
