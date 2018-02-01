"""
simple example script for running notebooks and saving the resulting notebook.

Usage: `execute_and_save.py foo.ipynb [bar.ipynb [...]]`

Each cell is submitted to the kernel, and the outputs are overwritten and 
stored in new notebooks foo_executed.ipynb, etc.
"""

import os,sys,time
import base64
import re

from collections import defaultdict
from Queue import Empty

from IPython.zmq.blockingkernelmanager import BlockingKernelManager
from IPython.nbformat.current import reads, NotebookNode

from nbconvert import ConverterNotebook

def compare_png(a64, b64):
    """compare two b64 PNGs (incomplete)"""
    try:
        import Image
    except ImportError:
        pass
    adata = base64.decodestring(a64)
    bdata = base64.decodestring(b64)
    return True

def sanitize(s):
    """sanitize a string for comparison.
    
    fix universal newlines, strip trailing newlines, and normalize likely random values (memory addresses and UUIDs)
    """
    # normalize newline:
    s = s.replace('\r\n', '\n')
    
    # ignore trailing newlines (but not space)
    s = s.rstrip('\n')
    
    # normalize hex addresses:
    s = re.sub(r'0x[a-f0-9]+', '0xFFFFFFFF', s)


    
    # normalize UUIDs:
    s = re.sub(r'[a-f0-9]{8}(\-[a-f0-9]{4}){3}\-[a-f0-9]{12}', 'U-U-I-D', s)
    
    return s


def compare_outputs(test, ref, skip_compare=('png', 'traceback', 'latex', 'prompt_number')):
    for key in ref:
        if key not in test:
            print "missing key: %s != %s" % (test.keys(), ref.keys())
            return False
        elif key not in skip_compare and sanitize(test[key]) != sanitize(ref[key]):
            print "mismatch %s:" % key
            print test[key]
            print '  !=  '
            print ref[key]
            return False
    return True


def run_cell(km, cell):
    shell = km.shell_channel
    iopub = km.sub_channel
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
    

def execute_notebook(nb):
    km = BlockingKernelManager()
    km.start_kernel(extra_arguments=['--pylab=inline'], stderr=open(os.devnull, 'w'))
    km.start_channels()
    # run %pylab inline, because some notebooks assume this
    # even though they shouldn't
    km.shell_channel.execute("pass")
    km.shell_channel.get_msg()
    while True:
        try:
            km.sub_channel.get_msg(timeout=1)
        except Empty:
            break
    
    successes = 0
    failures = 0
    errors = 0
    prompt_number = 1
    for ws in nb.worksheets:
        for cell in ws.cells:
            cell.prompt_number = prompt_number
            if cell.cell_type != 'code':
                continue
            try:
                outs = run_cell(km, cell)
            except Exception as e:
                print "failed to run cell:", repr(e)
                print cell.input
                errors += 1
                continue
            
            cell.outputs = outs
            prompt_number += 1
    km.shutdown_kernel()
    del km

def execute_and_save(ipynb):
    converter = ConverterNotebook(ipynb, os.path.splitext(ipynb)[0] + '_executed')
    converter.read()
    execute_notebook(converter.nb)    
    converter.render()


if __name__ == '__main__':
    for ipynb in sys.argv[1:]:
        print "executing %s" % ipynb
        execute_and_save(ipynb)

