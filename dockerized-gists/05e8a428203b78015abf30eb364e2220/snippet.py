class MockWriter(object):
    def write_file(self, path, contents):
      print "ooh look at me, i'm a file writer"
      print "i perform slow operations and sometimes i fail for no good reason"
      print "you only use me when you don't have a Real Database to talk to"
      print "I'm so cool! not!"
      return 0
