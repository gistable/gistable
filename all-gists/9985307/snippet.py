import sys, os
import ROOT as r
# prohibit root from hijacking command-line args
r.PyConfig.IgnoreCommandLineOptions = True

try:
  ROOTCORE_PATH = os.environ['ROOTCOREDIR']
except KeyError:
  print >>sys.stderr, "Warning! $ROOTCOREDIR env. variable is not set. Did you configure RootCore?"
  ROOTCORE_PATH = None

''' Decorator for methods that should only be run once. '''
def run_once(f):
  def wrapper(*args, **kwargs):
    if not wrapper.has_run:
      wrapper.has_run = True
      return f(*args, **kwargs)
  wrapper.has_run = False
  return wrapper

'''
 Call this method anytime you're going to use code that requires one of the
 libraries managed by RootCore. You can call it as many times as you want;
 the first one loads and subsequent calls will be a no-op.
'''
@run_once
def require_rootcore():
  r.gROOT.ProcessLine('.x %s' % os.path.join(ROOTCORE_PATH, 'scripts', 'load_packages.C'))