#!/usr/bin/python

import os

#globals
top = "/home/zuch/WWW/translate/archive" #root directory of archive

#node class
class node:
  path = ""
  depth = ""
  dirs = []
  files = []
  
  def __init__(self,path,depth,dirs,files):
    self.path = path
    self.depth = depth
    self.dirs = dirs
    self.files = files


#returns array of node objects for a given path
def parse(path):
  
  dir_list = []
  startinglevel = path.count(os.sep)
  
  for path, dirs, files in os.walk(path):
    depth = path.count(os.sep) - startinglevel
    Node = node(path,depth,dirs,files)
    dir_list.append(Node)
    
  return dir_list  
#-----------------------------------Main---------------------------------------        
if __name__ == "__main__":
  nodes = parse(top)
    
  i = 0
  for node in nodes:
    print "path:", node.path
    print "depth:",node.depth
    print "dirs:",node.dirs
    print "files:",node.files
    i += 1
    if(i >= 4):
      break
  
  
  