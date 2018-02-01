"""
Add copy to clipboard from IPython!
To install, just copy it to your profile/startup directory, typically:

    ~/.ipython/profile_default/startup/

Example usage:

    %clip hello world
    # will store "hello world"
    a = [1, 2, 3]
    %clip a
    # will store "[1, 2, 3]"

You can also use it with cell magic

    In [1]: %%clip
       ...: Even multi
       ...: lines
       ...: work!
       ...:

If you don't have a variable named 'clip' you can rely on automagic:

    clip hey man
    a = [1, 2, 3]
    clip a

"""

import sys

if sys.platform == 'darwin':
    from AppKit import NSPasteboard, NSArray
elif sys.platform.startswith('linux'):
    from subprocess import Popen, PIPE
else:
    raise ImportError("Clip magic only works on osx or linux!")

from IPython.core.magic import register_line_cell_magic

def _copy_to_clipboard(arg):
    arg = str(globals().get(arg) or arg)

    if sys.platform == 'darwin':
        pb = NSPasteboard.generalPasteboard()
        pb.clearContents()
        a = NSArray.arrayWithObject_(arg)
        pb.writeObjects_(a)
    elif sys.platform.startswith('linux'):
        p = Popen(['xsel', '-pi'], stdin=PIPE)
        p.communicate(input=arg)

    print 'Copied to clipboard!'


@register_line_cell_magic
def clip(line, cell=None):
    if line and cell:
        cell = '\n'.join((line, cell))

    _copy_to_clipboard(cell or line)

# We delete it to avoid name conflicts for automagic to work
del clip
