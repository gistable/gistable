#!/usr/bin/env python
"""
Interactive execution with automatic history, tries to mimic Mathematica's
prompt system. This environment's main features are:

- Numbered prompts (In/Out) similar to Mathematica. Only actions that produce
  output (NOT assingments, for example) affect the counter and cache.

- The following GLOBAL variables always exist (so don't overwrite them!):
  _p: stores previous result which generated printable output.
  _pp: next previous
  _ppp: next-next previous
  _cache[]: cache of all previous output, indexed by prompt counter.
  _pc: short alias for _cache

- Global variables named _p<n> are dynamically created (<n> being the
  prompt counter), such that the following is always true:
                       _p<n> == _pc[<n>]
  E.g. the 4th result is always available as either _pc[4] or as _p4.

Use help() to open Python's builtin help system, which can also be
called with optional keywords as arguments.

If you are running inside an Emacs buffer, use doc() as dumb-terminal
simpler version of help() [doesn't do all that help() does, though].

Current configuration (set _load.. variables to 0 to turn off):

Control loading of Numerical Python modules: _load_Numeric = %(_load_Numeric)s
Gnuplot Globals GP and gp (module/instance): _load_Gnuplot = %(_load_Gnuplot)s
Load gracePlot (2D-plotting only)        : _load_gracePlot = %(_load_gracePlot)s
Globals for SI units (including g=9.8)     : _load_units   = %(_load_units)s
Starting number for prompt counter         : _prompt_ini   = %(_prompt_ini)s
Number of history items to store in cache  : _cache_size   = %(_cache_size)s """

#****************************************************************************
# Configure here
_load_Numeric   = 1
_load_Gnuplot   = 1
_load_gracePlot = 1
_load_units     = 1
_cache_size     = 1000
_prompt_ini     = 1

# *** Don't modify below unless you know what you're doing. ***

# Crude first version, with minimal object structure. This could be done much
# better, by defining a Cache class (probably using weak references or
# generators). But it seems to work ok. Haven't checked for memory circularity
# problems, though.

#****************************************************************************
#       Copyright (C) 2001 Fernando Pérez. <fperez@pizero.colorado.edu>
#
#   Distributed under the terms of the GNU General Public License.
#
#   The full text of the GPL is available at:
#
#                  http://www.gnu.org/copyleft/gpl.html
#****************************************************************************
__author__ = 'Fernando Pérez. <fperez@pizero.colorado.edu>'
__version__= '0.1'

#****************************************************************************
# Class definitions

class _HistPrompt1:
    """Simple interactive prompt like Mathematica's."""
    def __str__(self):
        return '\nIn['+`_prompt_count`+']:= '

class _HistPrompt2:
    """Simple interactive continuation prompt."""
    def __str__(self):
        return '...'+' '*(len('In['+`_prompt_count`+']:= ')-3)

#****************************************************************************
# Function definitions

def _history_print(arg):
    """Printing with history cache management.

    This is invoked everytime the interpreter needs to print, and is activated
    by setting the variable sys.displayhook to it."""

    global _p,_pp,_ppp,_cache,_prompt_count

    # cleanup cache if needed
    if _prompt_count > _cache_size:
        print '\nWARNING: History cache size limit (currently '+\
              `_cache_size`+') hit.'
        print 'Flushing cache and resetting history counter...'
        print 'The only history variable available will be _p with current result.'
        print 'Increase the variable _cache_size if you need a larger cache.'
        _prompt_count = _prompt_ini
        _cache = []
        _p,_pp,_ppp = '','',''
        # fill bottom of cache if initial offset is not zero
        for n in range(_prompt_ini): _cache.append(None)
        # delete auto-generated vars from global namespace
        for n in range(_prompt_ini,_cache_size):
            exec 'del _p'+`n` in globals()
    # update cache
    _cache.append(arg)
    _ppp = _pp
    _pp = _p
    _p = arg
    exec '_p'+`_prompt_count`+'=_cache[-1]' in globals()
    print '\nOut['+`_prompt_count`+']=',arg
    _prompt_count += 1
# end of _history_print()

#----------------------------------------------------------------------------
def intro():
    """Show global docstring and config info."""
    print __doc__ % globals()

#----------------------------------------------------------------------------
def dgrep(pat,*opts):
    """Return grep() on dir()+dir(__builtins__).
    
    A very common use of grep() when working interactively."""

    exec 'data = dir()+dir(__builtins__)' in globals()
    return grep(pat,data,*opts)
# end of dgrep()

#----------------------------------------------------------------------------
def idgrep(pat):
    """Case-insensitive dgrep()"""

    exec 'data = dir()+dir(__builtins__)' in globals()
    return grep(pat,data,case=0)
# end of dgrep()

#-----------------------------------------------------------------------------
def Gnuplot_setup():
    
    """Setup some convenient globals for Gnuplot plotting, including a global
    gp Gnuplot object, ready for use."""

    global GP,gp

    GP = Gnuplot
    gp = GP.Gnuplot()  # global plotting process
    gp.logx = 'set logscale x'
    gp.logy = 'set logscale y'
    gp.nolog = 'set nologscale'
    gp.points = 'set data style points'
    gp.lines = 'set data style lines'
    gp.linesp = 'set data style linespoints'
    gp.errorbars = 'set data style errorbars'
# end of Gnuplot_setup()

#-----------------------------------------------------------------------------
def SI_Units():
    """Define some globals for physical units and constants.

    The following become available:

      g,mm,cm,km,gm,s,sec,hr,day,year,deg,ft,lb,inch

    These can be overwritten at any time. Calling SI_Units() again will reset
    their values if needed.  """

    global g,mm,cm,km,gm,s,sec,hr,day,year,deg,ft,lb,inch

    # physical constants
    g = 9.8
    
    # units
    mm = 0.001 # length
    cm = 0.01
    km = 1000.
    gm = 0.001 # mass
    s,sec = 1.,1.  # time
    hr = 3600.
    day = 24*hr
    year = 365*day
    deg = pi/180. # angles
    inch = 0.0254 # british
    ft = 12*inch
    lb = 0.454
# end of SI_Units()

#-----------------------------------------------------------------------------
def import_fail_info(mod_name):
    """Inform load failure for a module."""

    print """
WARNING: Loading of %(mod_name)s-related modules failed.
Fix your configuration or set _load_%(mod_name)s to 0 to prevent
seeing this message every time.
""" % vars()
    

#****************************************************************************
# Setup everything at global level for history system to work

# Python standard modules
import sys
from math import *
# Other modules
from Itpl import Itpl   # available at http://web.lfw.org/python/Itpl15.py
from genutils import *

# User-controlled modules and globals-affecting functions

if _load_Numeric:
    try:
        from Numeric import *  # Numeric *must* come after math.
        from numutils import *
        # useful for testing infinities in results of array divisions
        # (which don't raise an exception)
        infty = Infinity = (array([1])/0.0)[0]
    except:
        import_fail_info('Numeric')

if _load_Gnuplot:
    try:
        import Gnuplot
        Gnuplot_setup()
    except:
        import_fail_info('Gnuplot')

if _load_gracePlot:
    try:
        from gracePlot import gracePlot
    except:
        import_fail_info('gracePlot')

if _load_units:
    SI_Units()

# pydoc doesn't exist in Python 2.0 (I think):
try:
    from pydoc import help
except:
    print "Module pydoc not found. help() function unavailable."

# Initialize cache
_p,_pp,_ppp = '','',''
_prompt_count = _prompt_ini
_pc = _cache = []  # _pc is just an alias
# fill bottom of cache if initial offset is not zero
for n in range(_prompt_ini): _cache.append(None)

# cleanup global namespace a bit
del import_fail_info,n

# Set in/out prompts and printing system
sys.displayhook = _history_print
sys.ps1 = _HistPrompt1()
sys.ps2 = _HistPrompt2()

# Startup info
print '\nPython',sys.version.split('\n')[0]
print '\nInteractive Python -- Type intro() for a brief explanation.'
#************************* end of file <ipython.py> ***********************