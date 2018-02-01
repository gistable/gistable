"""Hackish script to convert a notebook into

Note that the content of markdown cells is not translated: it is assumed to
hold asciidoc content instead (even if it does not render correctly in the
browser editing the notebook file).

This script could be improved to use pandoc to handle the conversion instead.

Sample usage:

To convert a notebook into an asciidoc chapter file::

  $ python ipynbhelper.py --convert notebooks/chapter-1-introduction.ipynb

The resulting file should be chapter-1-introduction.asciidoc

To re-render all the code cells output prior to converting to asciidoc:

  $ python ipynbhelper.py --render --convert notebooks/chapter-1-introduction.ipynb

The matplotlib plots can be rendered inline the notebook with::

  % matplotlib inline
  import matplotlib.pyplot as plt

ipynbhelper.py will extract the inline plots as png files in the images/ folder
and generate asciidoc figure block for those images.

Code cells that include a plot should have a title (mandatory for asciidoc
figures) with their last line starting with "# title: ", for instance:

    plt.plot(range(10), label='Linear growth')
    plt.plot([x ** 2 for x in range(10)], label='Quadratic growth')
    plt.legend()
    # title: Comparing growth functions

Credits: this is derived from a mix of various gists by @minrk.

"""
from __future__ import print_function
from copy import deepcopy
import re
import sys
import os
import io
import base64
from Queue import Empty
from uuid import uuid4

from IPython.nbformat import current
try:
    from IPython.kernel import KernelManager
    assert KernelManager  # to silence pyflakes
except ImportError:
    # 0.13
    from IPython.zmq.blockingkernelmanager import BlockingKernelManager
    KernelManager = BlockingKernelManager


CODE_CELL_START = "// code cell start uuid: "
CODE_CELL_END = "// code cell end"

ASCIIDOC_BLOCK = "----\n"

MISSING_FIGURE_TITLE = "XXX: missing figure title"


def remove_outputs(nb):
    """Remove the outputs from a notebook"""
    for ws in nb.worksheets:
        for cell in ws.cells:
            if cell.cell_type == 'code':
                cell.outputs = []
                if 'prompt_number' in cell:
                    del cell['prompt_number']


def check_uuid(nb, cell_types=('code',)):
    """Add uuid tags to all the cell"""
    for ws in nb.worksheets:
        for cell in ws.cells:
            if cell.cell_type in cell_types:
                if not 'uuid' in cell.metadata:
                    cell.metadata['uuid'] = str(uuid4())


def run_cell(shell, iopub, cell, timeout=300):
    # print cell.input
    shell.execute(cell.input)
    # wait for finish, maximum 5min by default
    reply = shell.get_msg(timeout=timeout)['content']
    if reply['status'] == 'error':
        failed = True
        print("\nFAILURE:")
        print(cell.input)
        print('-----')
        print("raised:")
        print('\n'.join(reply['traceback']))
    else:
        failed = False

    # Collect the outputs of the cell execution
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
        out = current.NotebookNode(output_type=msg_type)

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
            print("unhandled iopub msg:", msg_type)

        outs.append(out)
    return outs, failed


def run_notebook(nb):
    km = KernelManager()
    km.start_kernel(stderr=open(os.devnull, 'w'))
    if hasattr(km, 'client'):
        kc = km.client()
        kc.start_channels()
        iopub = kc.iopub_channel
    else:
        # IPython 0.13 compat
        kc = km
        kc.start_channels()
        iopub = kc.sub_channel
    shell = kc.shell_channel

    # simple ping:
    shell.execute("pass")
    shell.get_msg()

    cells = 0
    failures = 0
    for ws in nb.worksheets:
        for cell in ws.cells:
            if cell.cell_type != 'code':
                continue

            outputs, failed = run_cell(shell, iopub, cell)
            cell.outputs = outputs
            cell['prompt_number'] = cells
            failures += failed
            cells += 1
            sys.stdout.write('.')

    print()
    print("ran notebook %s" % nb.metadata.name)
    print("    ran %3i cells" % cells)
    if failures:
        print("    %3i cells raised exceptions" % failures)
    kc.stop_channels()
    km.shutdown_kernel()
    del km


class Node(object):

    def __init__(self):
        self.lines = []
        self.images = []
        self.next_node = None

    def connect(self, next_node):
        self.next_node = next_node
        return next_node


def _clean_output_lines(text):
    first_line = True
    trimmed_lines = []
    for line in text.split('\n'):
        if first_line and not line.strip():
            continue

        # Discard matplotlib objects
        if "<matplotlib." in line:
            continue
        if "<Container object" in line:
            continue
        if "ticklabel" in line:
            continue

        trimmed_lines.append(line + '\n')
        first_line = False
    return trimmed_lines


class CodeNode(Node):

    def __init__(self, asciidoc_metadata=None):
        super(CodeNode, self).__init__()
        self.asciidoc_metadata = asciidoc_metadata

    def with_code_cell(self, cell):
        uuid = cell.metadata.uuid
        code = cell.input
        code = re.sub(' +\n', '\n', code)  # trim eol whitespaces
        code_lines = code.split('\n')
        self.lines = []
        figure_title = MISSING_FIGURE_TITLE
        has_figure = False
        self.lines.append(CODE_CELL_START + '%s\n' % uuid)
        if self.asciidoc_metadata != "skip_input":
            self.lines.append('[source,python]\n')
            self.lines.append('----\n')
            for code_line in code_lines:
                if code_line.startswith('# title: '):
                    figure_title = code_line[len('# title: '):]
                    has_figure = True
                else:
                    self.lines.append(code_line + '\n')
            self.lines.append('----\n\n')
        else:
            # scan for the title
            for code_line in code_lines:
                if code_line.startswith('# title: '):
                    figure_title = code_line[len('# title: '):]
        img_idx = 0
        in_stream = False
        for output in cell.outputs:
            if output.output_type in ("stream", "pyout"):
                if (output.output_type == "pyout" and has_figure):
                    # skip matplotlib object representation
                    # Hack: this breaks if we want to display a python object
                    # and a plot in the same cell but do we care?
                    continue
                output_lines = _clean_output_lines(output.text)
                if len(output_lines) > 0:
                    if not in_stream:
                        self.lines.append(ASCIIDOC_BLOCK)
                        in_stream = True
                    self.lines.extend(output_lines)
            elif output.output_type == "display_data":
                if in_stream:
                    self.lines.append(ASCIIDOC_BLOCK)
                    self.lines.append('\n')
                    in_stream = False
                if 'png' in output:
                    img_name = "images/%s-%03d.png" % (uuid, img_idx)
                    img_bytes = base64.decodestring(output.png)
                    self.images.append((img_name, img_bytes))
                    self.lines.append('[[' + uuid.replace('-', '_') + ']]\n')
                    self.lines.append('.' + figure_title + '\n')
                    img_line = 'image::%s[scale="75"]\n' % img_name
                    self.lines.append(img_line)
                    self.lines.append('\n')
                    img_idx += 1
        if in_stream:
            if self.lines[-1] == '\n':
                self.lines.pop()
            self.lines.append(ASCIIDOC_BLOCK)
            self.lines.append('\n')
        self.lines.append(CODE_CELL_END + '\n\n')
        return self


class AsciidDoc(object):

    def __init__(self, filename=None):
        self.first_node = current_node = Node()
        self.filename = filename
        self.uuid_nodes = {}

        if filename is not None:
            with open(filename, 'rb') as f:
                line_iterator = iter(f)
                for line in line_iterator:
                    if (line.startswith(CODE_CELL_START)):
                        uuid = line[len(CODE_CELL_START):].strip()
                        current_node = current_node.connect(CodeNode())
                        current_node.lines.append(line)
                        self.uuid_nodes[uuid] = current_node

                    elif line.startswith(CODE_CELL_END):
                        current_node.lines.append(line)
                        try:
                            # CODE_CELL_END has two line returns
                            current_node.lines.append(line_iterator.next())
                        except StopIteration:
                            pass
                        current_node = current_node.connect(Node())
                    else:
                        current_node.lines.append(line)

    def get_last_node(self):
        current_node = self.first_node
        while current_node.next_node is not None:
            current_node = current_node.next_node
        return current_node

    def merge_code_from(self, nb):
        where_to_append = self.get_last_node()
        for ws in nb.worksheets:
            for cell in ws.cells:
                if cell.cell_type == 'code':
                    asciidoc_metadata = cell.metadata.get('asciidoc')
                    if asciidoc_metadata == "skip":
                        continue
                    uuid = cell.metadata.setdefault('uuid', str(uuid4()))
                    uuid_node = self.uuid_nodes.get(uuid)
                    if uuid_node is not None:
                        uuid_node.with_code_cell(cell)
                        where_to_append = uuid_node
                    else:
                        new_node = CodeNode(asciidoc_metadata)
                        new_node.with_cell(cell)
                        where_to_append = where_to_append.connect(new_node)

    def convert_from(self, nb):
        current_node = self.first_node
        for ws in nb.worksheets:
            for cell in ws.cells:
                if cell.cell_type == 'code':
                    asciidoc_metadata = cell.metadata.get('asciidoc')
                    if asciidoc_metadata == "skip":
                        continue
                    cell.metadata.setdefault('uuid', str(uuid4()))
                    new_node = CodeNode(asciidoc_metadata).with_code_cell(cell)
                    current_node = current_node.connect(new_node)
                elif cell.cell_type == 'markdown':
                    current_node = current_node.connect(Node())
                    source = re.sub(' +(\n|$)', '\n', cell.source)
                    if not source.endswith('\n'):
                        source += '\n'
                    current_node.lines.append(source)
                    current_node.lines.append('\n')
                elif cell.cell_type == 'heading':
                    current_node = current_node.connect(Node())
                    heading = '=' * (cell.level + 1) + " " + cell.source + '\n'
                    current_node.lines.append('\n')
                    current_node.lines.append(heading)
                    current_node.lines.append('\n')

    def save(self, filename=None):
        if filename is None:
            filename = self.filename
        current_node = self.first_node
        base_folder = os.path.dirname(filename)
        with open(filename, 'wb') as f:
            # Save the main asciidoc file
            while current_node is not None:
                for line in current_node.lines:
                    f.write(line.encode('utf-8'))

                # Save auxiliary files
                for img_name, img_bytes in current_node.images:
                    img_path = os.path.join(base_folder, img_name)
                    folder = os.path.dirname(img_path)
                    if not os.path.exists(folder):
                        os.makedirs(folder)
                    with open(img_path, 'wb') as img_f:
                        img_f.write(img_bytes)

                current_node = current_node.next_node


def process_notebook_file(fname, actions=('clean',), asciidoc_fname=None):
    print("Performing '{}' on: {}".format("', '".join(actions), fname))

    orig_wd = os.getcwd()
    os.chdir(os.path.dirname(fname))

    with io.open(fname, 'rb') as f:
        nb = current.read(f, 'json')

    if 'uuid' in actions:
        check_uuid(nb)

    if 'render' in actions:
        run_notebook(nb)
    elif 'check' in actions:
        run_notebook(deepcopy(nb))

    if 'clean' in actions:
        remove_outputs(nb)

    if 'merge' in actions:
        doc = AsciidDoc(asciidoc_fname)
        doc.merge_code_from(nb)
        doc.save()
    elif 'convert' in actions:
        doc = AsciidDoc()
        doc.convert_from(nb)
        doc.save(asciidoc_fname)

    os.chdir(orig_wd)

    with io.open(fname, 'wb') as f:
        current.write(nb, f, 'json')


if __name__ == '__main__':
    # TODO: use argparse instead
    args = sys.argv[1:]
    targets = [t for t in args if not t.startswith('--')]
    actions = [a[2:] for a in args if a.startswith('--')]
    if not actions:
        print('Please specify actions to perform')
        sys.exit(1)

    if not targets:
        targets = [os.path.join(os.path.dirname(__file__), 'notebooks')]

    for target in targets:
        if os.path.isdir(target):
            fnames = [os.path.abspath(os.path.join(target, f))
                      for f in os.listdir(target)
                      if f.endswith('.ipynb')]
        else:
            fnames = [os.path.abspath(target)]
        for fname in fnames:
            if 'merge' in actions or 'convert' in actions:
                asciidoc_fname = os.path.basename(fname)[:-len('.ipynb')]
                asciidoc_fname += '.asciidoc'
                asciidoc_fname = os.path.join(os.path.dirname(fname),
                                              '..',
                                              asciidoc_fname)
            else:
                asciidoc_fname = None
            process_notebook_file(fname, actions=actions,
                                  asciidoc_fname=asciidoc_fname)
