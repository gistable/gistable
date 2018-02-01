import traceback

def printexceptions(f):
  def a(*args, **kwargs):
    try:
      return f(*args, **kwargs)
    except:
      traceback.print_exc()
  return a

@printexceptions
def testfunction(asdf):
  raise Exception("This is an exception.")

@printexceptions
def testfunction2():
  return 2

try:
  testfunction('derpaderp')
except:
  print "This exception handler should never be reached."

assert(testfunction2() == 2)
