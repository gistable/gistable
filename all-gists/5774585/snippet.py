#!/usr/bin/python
#
# Given a line number, leave only the frame that covers the line number
# and invoke pdflatex. It is a nice way to preview one beamer slide,
# when the whole presentation is compiling for a couple of minutes.
#
# The preprocessor is very simple, if something breaks, let me know.
# To work properly with included files, we are using latexexpand.pl
# by Matthieu Moy.
#
# MULTIPLE FILES
#
# If you keep the frames in multiple files, specify the main file
# in the first line of each sub-file as follows:
# 
# % main: my-main-file.tex
#
# USING WITH VIM
#
# This is how you can bind the preview on Ctrl-p in ~/.vimrc:
#
# nmap <C-p> :execute "!beamer-preview " . expand("%") . " " . line(".")<CR>
#
# USING WITH EMACS
#
# Define the following mapping ~/.emacs (thanks, Josef Widder):
#
# (defun beamerpreview ()
#  (interactive "*")
#    (shell-command (format "beamer-preview %s %d"
#                    (buffer-file-name)
#                    (1 + (count-lines 1 (point))))))
# (global-set-key "\C-c\C-n" 'beamerpreview)
#
# You will find the preview slide in preview.pdf
#
# Igor Konnov <konnov at forsyte.at>, 2013-2015

import re
import os
import shutil
import subprocess
import sys
import tempfile

from StringIO import StringIO

STATE_OUT_FRAME = 0
STATE_IN_FRAME = 1
AGAIN_FRAME_RE = re.compile(r'^(.*?)\\againframe[^{]*{[^}]*}(.*)$')
MAIN_RE = re.compile(r'^\s*%\s*main:\s*(.*)$')
# this regex is copied from latexexpand by Matthieu Moy
INPUT_RE = re.compile(r'^[^%\\]*\\input[{\s]+(.*?)[\s}].*$')


class InputError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


# similar to that in latexexpand
def find_file(parent, name):
    if os.path.isabs(name) and os.path.isfile(name):
        return name

    (parent_dir, _) = os.path.split(parent)
    full_name = os.path.join(parent_dir, name)
    if os.path.isfile(full_name):
        return full_name
    else:
        return None


def find_tex_file(parent, name):
    full = find_file(parent, name)
    if full:
        return full
    else:
        full = find_file(parent, name + '.tex')
        if full:
            return full
        else:
            (parent_dir, _) = os.path.split(parent)
            raise InputError("Input file %s not found in %s" % (name, parent_dir))


def exclude_slides(out, filename, keep_filename, keep_line_no):
    keep = (os.path.realpath(filename) == os.path.realpath(keep_filename))

    state = STATE_OUT_FRAME
    lineno, start_lineno, end_lineno = 1, -1, -1

    f = open(filename, "r")
    for line in f:
        line = line.rstrip('\n')
        line = line.rstrip('\r')
        m = INPUT_RE.match(line)
        if m:
            if state == STATE_IN_FRAME:
                fo = frame # write to the frame buffer
            else:
                fo = out   # write to out directly

            included_name = find_tex_file(filename, m.group(1))
            fo.write('\makeatletter{}\n%% input  %s:%d\n' % (included_name, lineno))
            exclude_slides(fo, included_name, keep_filename, keep_line_no)
            fo.write('%% end of %s:%d\n' % (included_name, lineno))
            fo.write(' \n') # following the wisdom of latexexpand
        elif line.find('\\begin{document}') >= 0:
            # change the title to preview
            out.write('  \\title{preview %s:%d}\n' % (keep_filename, keep_line_no))
            out.write(line)
        elif line.find('\\begin{frame}') >= 0:
            state = STATE_IN_FRAME
            start_lineno = lineno
            frame = StringIO('')
            frame.write(line)
        elif line.find('\\end{frame}') >= 0:
            state = STATE_OUT_FRAME
            end_lineno = lineno
            if keep and start_lineno <= keep_line_no and keep_line_no <= end_lineno:
                # flush the selected frame
                out.write(frame.getvalue())
                out.write(line)
            else:
                out.write('%% forwarded to line %s:%d\n' % (filename, lineno))

            frame.close()
        elif state == STATE_OUT_FRAME:
            # remove \againframe{...}
            m = AGAIN_FRAME_RE.match(line)
            if m:
                out.write(m.group(1))
                out.write(m.group(2))
                out.write('\n')
            else:
                out.write(line)
                out.write('\n')
        elif state == STATE_IN_FRAME:
            frame.write(line)
            frame.write('\n')
        else:
            assert(False) # should not reach here

        lineno += 1

    f.close()


def find_main(filename):
    """Read the first line and if it looks like '% main: ...',
       return the file specified there. Otherwise, return the
       argument."""

    with open(filename, 'r') as f:
        line = f.readline()
        m = MAIN_RE.match(line)
        if m:
            main = m.group(1).strip()
            if os.path.isabs(main):
                return main
            else:
                dirname, _ = os.path.split(filename)
                return os.path.join(dirname, main)
        else:
            return filename


if __name__ == "__main__":
    try:
        filename = sys.argv[1]
        user_lineno = int(sys.argv[2])
    except IndexError:
        print "Use: %s file.tex lineno" % sys.argv[0]
        sys.exit(1)

    main = find_main(filename)
    print "Starting with main: %s" % main
    tmpdir = tempfile.mkdtemp(prefix = '_preview.')
    out = open(os.path.join(tmpdir, 'preview.tex'), 'w')
    exclude_slides(out, main, filename, user_lineno)
    out.write('%% end of main %s\n' % filename)
    out.close()
    subprocess.call(["pdflatex", "-output-directory", tmpdir,
        "-halt-on-error", "-file-line-error", "preview.tex"])
    shutil.copy(os.path.join(tmpdir, "preview.pdf"), "preview.pdf")
    shutil.rmtree(tmpdir)

