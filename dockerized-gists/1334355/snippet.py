import sys

"""
Save this file as c:\Python24\Lib\docprint.py or in your application or library directory.

File is maintained as a gist at github: https://gist.github.com/1334355
"""


def write(txt):
  sys.stderr.write(txt)

def writeln(txt=""):
  write(txt)
  write("\n")


def header(txt):
  l = len(txt)
  writeln() 
  writeln(txt) 
  writeln("-" * l) 
  writeln() 

def listmember_maxlen(list1):
  max = 0
  for e in list1:
    sl = len(e)
    if sl > max:
      max = sl
  return max 


class C(object):

  def __init__(self):
    self.lines=0
    self.blocks=0
    
  def write_greeting(self):
    write("\n### START FILE ###\n")
    self.lines=self.lines+3

  def nextblockid(self):
    self.blocks=self.blocks+1
    sbs = "0%s" % self.blocks
    sbs = sbs [-2:]
    write("\n(%s) " % sbs)


  def done(self):
    writeln(" done.")
    ++self.lines

  def start(self,txt):
    if self.lines == 0:
      self.write_greeting()
    self.nextblockid()
    write(txt)
    write(" ... ")
  
  
  def kv_list(self,dict1,indent="  "):
    keys = dict1.keys()
    max_keylen = listmember_maxlen(keys)
    keys.sort() 
    for k in keys:
      tabbed_key = ("%s             " % k)[:max_keylen] 
      writeln("""%s'%s' : '%s'""" % (indent,tabbed_key,dict1[k]))    
              
c=C()

def P(txt=None,obj1=None):
  if txt is None:
    c.done()
    return
  if obj1 is None:    
    c.start(txt)
    return
  header(txt)
  c.kv_list(obj1.__dict__)
  
  
