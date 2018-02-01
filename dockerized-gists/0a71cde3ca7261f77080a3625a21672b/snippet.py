# Copyright 2016 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Routines for multi-threaded i/o."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys
import threading


def walk(top, threads=60):
  """Multi-threaded version of os.walk().

  This routine provides multiple orders of a magnitude performance improvement
  when top is mapped to a network filesystem where i/o operations are slow, but
  unlimited. For spinning disks it should still run faster regardless of thread
  count because it uses a LIFO scheduler that guarantees locality. For SSDs it
  will go tolerably slower.

  The more exotic coroutine features of os.walk() can not be supported, such as
  the ability to selectively inhibit recursion by mutating subdirs.

  Args:
    top: Path of parent directory to search recursively.
    threads: Size of fixed thread pool.

  Yields:
    A (path, subdirs, files) tuple for each directory within top, including
    itself. These tuples come in no particular order; however, the contents of
    each tuple itself is sorted.
  """
  if not os.path.isdir(top):
    return
  lock = threading.Lock()
  on_input = threading.Condition(lock)
  on_output = threading.Condition(lock)
  state = {'tasks': 1}
  paths = [top]
  output = []

  def worker():
    while True:
      with lock:
        while True:
          if not state['tasks']:
            output.append(None)
            on_output.notify()
            return
          if not paths:
            on_input.wait()
            continue
          path = paths.pop()
          break
      try:
        dirs = []
        files = []
        for item in sorted(os.listdir(path)):
          subpath = os.path.join(path, item)
          if os.path.isdir(subpath):
            dirs.append(item)
            with lock:
              state['tasks'] += 1
              paths.append(subpath)
              on_input.notify()
          else:
            files.append(item)
        with lock:
          output.append((path, dirs, files))
          on_output.notify()
      except OSError as e:
        print(e, file=sys.stderr)
      finally:
        with lock:
          state['tasks'] -= 1
          if not state['tasks']:
            on_input.notifyAll()

  workers = [threading.Thread(target=worker,
                              name="fastio.walk %d %s" % (i, top))
             for i in range(threads)]
  for w in workers:
    w.start()
  while threads or output:  # TODO(jart): Why is 'or output' necessary?
    with lock:
      while not output:
        on_output.wait()
      item = output.pop()
    if item:
      yield item
    else:
      threads -= 1
