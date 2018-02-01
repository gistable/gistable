import datetime

class Timer:
  def __init__(self, string=None):
    self.string = string

  def __enter__(self):
    self.t1 = datetime.datetime.now()

  def __exit__(self, exc_type, exc_value, traceback):
    self.t2 = datetime.datetime.now()
    if self.string:
      print (self.string + " seconds elapsed %f") % (self.t2 - self.t1).total_seconds()
    else:
      print "Seconds elapsed %f" % (self.t2 - self.t1).total_seconds()
    
      
if __name__ == '__main__':
  import csv, sys
  with Timer("Opening file"):
    with open("file.txt") as fh:
      reader = csv.reader(fh)
      data = [r for r in reader]
      