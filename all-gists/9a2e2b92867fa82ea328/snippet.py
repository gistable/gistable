melfunction.py
"""
Provides tools for wrapping mel commands for more Pythonic access.

Note this is a supplement to maya.cmds, not a replacement for it! This is intended to provide 
similar coverage for un-translated MEL or commands fron plugins which don't respect the 
ordinary cmds conventions.

Legalese:
 
Copyright (c) 2014 Steve Theodore
 
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""


import maya.mel

def run_mel(cmd, *args, **kwargs):
    """
    Run the supplied mel command with the supplied arguments and keyword arguments. It's intended
    to allow MEL or plugin-based commands which don't abide by the maya.cmds syntax rules to 
    look and act as much like Python as possible.
    
    Usage:
    
        run_mel("FBXExportBakeComplexEnd", v = end_frames[x])

    Return:
        passes the return value from the mel command
    
    Known limitation: does not support multi-use flags
    """
    # makes every value into a tuple or list so we can string them together easily
    unpack = lambda v: v if hasattr(v, '__iter__') else (v,)
    output = []
    for k, v in kwargs.items(): 
        output.append ("-%s" % k)
        # if the flag value is True of False, skip it 
        if not v in (True, False):
            output.extend (unpack(v))

    for arg in args:
        output.append (arg)

    quoted = lambda q: '"%s"' % str(q)

    return maya.mel.eval("%s(%s)" % (cmd, ", ".join(map(quoted, output))))
    
def mel_cmd(cmd):
    """
    Creates a function object which calls the string 'cmd' using run_mel.  This allows the creation of 
    functions which look and act like other Python commands, even though they run Mel under the hood.
    
    usage:
       
       FBXExport = mel_cmd("FBXExport")    
       FBXExport(f = "this_is_a_lot_nicer.fbx")
       
    The best practice is to create module which uses this pattern to define commands and import them into other code, 
    rather than creating the function objects in-line with other code. Both techniques work, but the former is simpler 
    to read and understand.
    """
    def wrap (*args, **kwargs):
        return run_mel(cmd, *args, **kwargs)
    return wrap