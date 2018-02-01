#!/usr/bin/env python
"""
Script for running and save notebooks from command line.

How to use: `ipynb_run_save.py foo.ipynb

Some tweaks over ipydoctest.py from minrk

by @damianavila
"""

import io
import os
import sys

from Queue import Empty

from IPython.kernel.blockingkernelmanager import BlockingKernelManager
from IPython.nbformat.current import read, write, NotebookNode


def run_cell(km, cell):
    shell = km.shell_channel
    iopub = km.iopub_channel
    # print "\n\ntesting:"
    # print cell.input
    shell.execute(cell.input)
    # wait for finish, maximum 20s
    shell.get_msg(timeout=20)
    outs = []

    while True:
        try:
            msg = iopub.get_msg(timeout=0.2)
        except Empty:
            break
        msg_type = msg['msg_type']
        if msg_type in ('status', 'pyin'):
            continue
        elif msg_type == 'clear_output':
            outs = []
            continue

        content = msg['content']
        # print msg_type, content
        out = NotebookNode(output_type=msg_type)

        if msg_type == 'stream':
            out.stream = content['name']
            out.text = content['data']
        elif msg_type in ('display_data', 'pyout'):
            for mime, data in content['data'].iteritems():
                attr = mime.split('/')[-1].lower()
                # this gets most right, but fix svg+html, plain
                attr = attr.replace('+xml', '').replace('plain', 'text')
                setattr(out, attr, data)
            if msg_type == 'pyout':
                out.prompt_number = content['execution_count']
        elif msg_type == 'pyerr':
            out.ename = content['ename']
            out.evalue = content['evalue']
            out.traceback = content['traceback']
        else:
            print "unhandled iopub msg:", msg_type

        outs.append(out)
    return outs


def test_notebook(nb):
    km = BlockingKernelManager()
    km.start_kernel(extra_arguments=['--pylab=inline'], stderr=open(os.devnull, 'w'))
    km.start_channels()
    # run %pylab inline, because some notebooks assume this
    # even though they shouldn't
    km.shell_channel.execute("pass")
    km.shell_channel.get_msg()
    while True:
        try:
            km.iopub_channel.get_msg(timeout=1)
        except Empty:
            break

    errors = 0
    cells = 0
    for ws in nb.worksheets:
        for cell in ws.cells:
            if cell.cell_type != 'code':
                continue
            cells += 1
            try:
                outs = run_cell(km, cell)
            except Exception as e:
                print "failed to run cell:", repr(e)
                print cell.input
                errors += 1
                continue
            cell.outputs = outs

    if errors:
        print "    %3i cells failed to complete" % errors
    if cells:
        print "%i code cells from notebook %s" % (cells, nb.metadata.name)
    km.shutdown_kernel()
    del km

if __name__ == '__main__':
    for ipynb in sys.argv[1:]:
        print "running %s" % ipynb
        with io.open(ipynb, encoding='utf8') as f:
            nb = read(f, 'json')
        test_notebook(nb)
        base, ext = os.path.splitext(ipynb)
        new_ipynb = "%s_run_saved%s" % (base, ext)
        with io.open(new_ipynb, 'w', encoding='utf8') as f:
            write(nb, f, 'json')
        print "wrote %s" % new_ipynb