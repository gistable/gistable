# coding: utf-8

import re as _re
import sys as _sys
import os



class WinSafeFileCreateError(Exception):
  pass


class WinSafeFileCreate(object):
  """
  Creates and returns the absolute path of the file given a relative or
  absolute path for windows systems.
  If any error occurs during path-processing, raises `WinSafeFileCreateError`
  """
  def __init__(self,_path):
    self.started_at = os.path.abspath(os.getcwd())
    dr,fo,fi = WinSafeFileCreate.get_all_paths(_path)
    dr,fo,fi = WinSafeFileCreate.validate_paths(dr,fo,fi)
    #if dr:
    #  self.final_path = dr+":\\"
    #else:
    #  self.final_path = ''
    #for i in fo:
    #  self.final_path+=(i+"\\")
    #self.final_path+=fi
    #print "FP:>",self.final_path
    self.final_file_abspath = WinSafeFileCreate.process_paths(dr,fo,fi, self.started_at)
  
  def __str__(self):
    return self.final_file_abspath
  
  @staticmethod
  def get_all_paths(p):
    dr = None
    fo = []
    fi = None

    if len(p)>3:
      if p[1:3] in [':/',':\\'] and _re.match(r'^[a-zA-Z]$',p[0]): #starts with drive
        if os.path.exists(p[:2]): # if drive exists
          dr = p[0]
          for i in _re.split('[\\\/]+|\\+|\/+', p[2:]):
            fo.append(i)
        else: # if drive does not exist
          raise WinSafeFileCreateError('\"'+p[:2]+'\" does not exists on this system.')
      else:
        ps = _re.split('[\\\/]+|\\+|\/+', p)
        if len(ps)<=1:
          fi = p.split(':')[0]
        else:
          for i in ps:
            fo.append(i)
    else:
      fi = p.split(':')[0]
    if folders:
      fi = fo.pop() # last fo element will be considered as filename
    return (dr, fo, fi)
  
  @staticmethod
  def validate_paths(dr,fo,fi):
    creatable = []
    for i in fo:
      if _re.match('^.*[\?\\\/\<\>\:\|\"\*]+.*$',i):
        raise WinSafeFileCreateError("Folder \""+i+"\" contains invalid character.")
      else:
        if not _re.match('^\.+$', i):
          creatable.append(i.lstrip('. ').rstrip('. '))
        else:
          creatable.append(i)

    if _re.match('^.*[\?\\\/\<\>\:\|\"\*]+.*$',fi):
      raise WinSafeFileCreateError("Filename \""+fi+"\" contains invalid character.")
    else:
      fi = fi.lstrip('. ').rstrip('. ')

    return (dr,creatable,fi)
      
  @staticmethod    
  def process_paths(dr,fo,fi,s):
    if dr: # if paths include directory
      os.chdir(dr+":")
      while len(os.getcwd())>3: # while not at the root folder of our drive
        os.chdir("..") # keep going back
    for i in fo:
      if i=='':
        continue
      elif i=='.':
        continue
      elif i=='..':
        os.chdir('..')
      elif _re.match(r'^\.{2,}$',i):
        continue
      else:
        try:
          os.chdir(i)
        except WindowsError as e:
          try:
            os.mkdir(i)
          except:
            os.chdir(s)
            raise WinSafeFileCreateError('Not enough permission to create folder: '+i)
          os.chdir(i)
        except:
          os.chdir(s)
          raise WinSafeFileCreateError('Unknown error occurred while processing paths.')
    try:
      open(fi,'w+').close()
      final_file_abspath = os.path.abspath(fi)
      os.chdir(s)
      return final_file_abspath
    except:
      os.chdir(s)
      raise WinSafeFileCreateError('Not enough permission to create file: '+fi)

win_test_paths = [
'.//.../fkdf/dkfd.jpg',
'CD:/fdkjiuero/elr/.jps',
'S:\\\\\\\\erker/dfl\\////k.ls',
'./........./.................../../\\\\\\\\\\\\\\\\\\\\\\\\\\\\pterte.jpg',
'|:',
'C:/big.dat'
]
for i in win_test_paths:
  try:
    print WinSafeFileCreate(i)
  except WinSafeFileCreateError as e:
    print e
    continue
    
__all__ = ['WinSafeFileCreate']