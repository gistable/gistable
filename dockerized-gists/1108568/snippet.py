import unittest, exceptions, pdb
class PDBAssertionError(exceptions.AssertionError):
  def __init__(self, *args):
    exceptions.AssertionError.__init__(self, *args)
    print "Assertion failed, entering PDB..."
    if hasattr(sys, '_getframe'):
      pdb.Pdb().set_trace(sys._getframe().f_back.f_back)
    else:
      pdb.set_trace()
unittest.TestCase.failureException = PDBAssertionError
