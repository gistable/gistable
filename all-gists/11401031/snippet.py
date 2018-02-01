#!/usr/bin/env python
"""Use inotify to watch a directory and execute a command on file change.

Watch for any file change below current directory (using inotify via pyinotify)
and execute the given command on file change.

Just using inotify-tools `while inotifywait -r -e close_write .; do something; done`
has many issues which are fixed by this tools:
 * If your editor creates a backup before writing the file, it'll trigger multiple times.
 * If your directory structure is deep, it'll have to reinitialize inotify after each change.
 * If your command takes time to execute and isn't in background, you may miss all file changes
   done during that command's execution; and if you run your command in background you may should
   make sure you can run it simultaneously multiple times.
 * File filtering becomes a small script (see also https://superuser.com/questions/181517/).

Install:
 1. Install pyinotify `$ pip install pyinotify` or `apt-get install python-pyinotify`.
 2. Save this script somewhere in your PATH, for example `~/bin/inotifyexec`
 3. `chmod +x inotifyexec`

Usage: inotifyexec echo test
"""

__author__ = "Werner Beroux <werner@beroux.com>"

import multiprocessing
import os.path
import sys
import threading
import time

try:
  import pyinotify
except ImportError:
  print('Python pyinotify package is missing (often named python-pyinotify).')
  sys.exit(1)


def watch_delay_call(
    base_directory,
    callback,
    delay=0.5,
    call_once_initially=True,
    mask=pyinotify.IN_DELETE | pyinotify.IN_CREATE | pyinotify.IN_CLOSE_WRITE |
    pyinotify.IN_MODIFY | pyinotify.IN_MOVED_TO):
  """Watch all files below a directory and execute a command on changes.

  Add some delay so that multiple save operations trigger a single execution.

  Example:
    def filechanged(paths):
      # TODO: Do something useful.
      print(paths)

    _watch_delay_call('.', filechanged)

  Args:
    base_directory: Directory to monitor, recursively.
    callback: Function to call on file change, with a list of paths.
    delay: Time in seconds to delay.
    call_once_initially: Set to true to call the callback once initially.
    mask: File system changes to listen for (by default any file change).
  """

  class Process(pyinotify.ProcessEvent):

    def __init__(self, immediate_callback):
      self.immediate_callback = immediate_callback

    def process_default(self, event):
      target = os.path.join(event.path, event.name)
      self.immediate_callback(target)

  def delay_call(pipe, delayed_callback, delay, call_once_initially):
    if call_once_initially:
      delayed_callback(None)

    path_list = []

    while True:
      # Wait until there is a change.
      path_list.append(pipe.recv())
      while pipe.poll():
        path_list.append(pipe.recv())

      # Delay
      time.sleep(delay)

      # If there are more changes, restart the timer.
      if pipe.poll():
        continue

      # Execute the callback.
      delayed_callback(path_list)

      path_list = []

  receiver, sender = multiprocessing.Pipe(False)

  delay_callback_thread = threading.Thread(
      target=delay_call,
      args=(receiver, callback, delay, call_once_initially))
  delay_callback_thread.daemon = True  # dies with this program.
  delay_callback_thread.start()

  while True:
    wm = pyinotify.WatchManager()
    notifier = pyinotify.Notifier(wm, Process(sender.send))
    wm.add_watch(base_directory, mask, rec=True, auto_add=True)
    try:
      while True:
        notifier.process_events()
        if notifier.check_events():
          notifier.read_events()
    except KeyboardInterrupt:
      notifier.stop()
      break


if __name__ == '__main__':
  import subprocess
  import re
  import argparse

  parser = argparse.ArgumentParser(description='Watch directory and execute command on file changes.')
  parser.add_argument('--filter', nargs='?', metavar='regex', help='only trigger for files matching the pattern.')
  parser.add_argument('command')
  parser.add_argument('arg', nargs='*')

  args = parser.parse_args()

  command_args = [args.command] + args.arg
  pattern = args.filter

  def callback(paths):
    if paths:
      if pattern:
        paths = [path for path in paths if re.search(pattern, path)]
        if not paths:
          return

      print('')
      for path in paths:
        print('  {0}'.format(path))
    print('\033[1m+ {0}\033[0m'.format(' '.join(['\'{0}\''.format(x) for x in command_args])))
    subprocess.call(command_args)
    print('\033[36mMonitoring file changes in {0}...\033[0m'.format(os.getcwd()))

  watch_delay_call('.', callback)
