import os, time, sys, fnmatch

path_to_watch = "D:/Projects/consumer-purchase-webapp/WebContent/js"

def findCoffeeFiles():
  matches = []
  for root, dirnames, filenames in os.walk(path_to_watch):
    for filename in fnmatch.filter(filenames, '*.coffee'):
      matches.append(os.path.join(root, filename))
  return matches


def out(str):
  print str
  sys.stdout.flush()


def findModified(before, after):
  modified = []
  for (bf,bmod) in before.items():
    if (after[bf] and after[bf] > bmod):
      modified.append(bf)
  return modified
      


out("HELLO")

before = dict ((f, os.path.getmtime(f)) for f in findCoffeeFiles())

while 1:
  time.sleep (1)
  after = dict ((f, os.path.getmtime(f)) for f in findCoffeeFiles())
  added = [f for f in after.keys() if not f in before.keys()]
  removed = [f for f in before.keys() if not f in after.keys()]
  modified = findModified(before,after)
  if added: out("Added: " + ", ".join (added))
  if removed: out("Removed: " + ", ".join (removed))
  if modified: out("Changed: " + ", ".join (modified))
  if (added or removed or modified):
    out("Recompiling...")
    os.chdir("D:/Projects/consumer-purchase-webapp/build")
    os.system("C:/apache-ant-1.7.0/bin/ant compileCoffeescripts")
  before = after


