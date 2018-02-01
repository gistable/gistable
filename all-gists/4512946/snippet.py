# Copyright (c) 2001-2004 Twisted Matrix Laboratories.
# See LICENSE for details.
# http://twistedmatrix.com/trac/browser/tags/releases/twisted-8.2.0/twisted/python/procutils.py?format=txt

"""
Utilities for dealing with processes.
"""

import os

def which(name, flags=os.X_OK):

  """Search PATH for executable files with the given name.
  
  On newer versions of MS-Windows, the PATHEXT environment variable will be
  set to the list of file extensions for files considered executable. This
  will normally include things like ".EXE". This fuction will also find files
  with the given name ending with any of these extensions.

  On MS-Windows the only flag that has any meaning is os.F_OK. Any other
  flags will be ignored.
  
  @type name: C{str}
  @param name: The name for which to search.
  
  @type flags: C{int}
  @param flags: Arguments to L{os.access}.
  
  @rtype: C{list}
  @param: A list of the full paths to files found, in the
  order in which they were found.
  """
  result = []
  exts = list(filter(None, os.environ.get('PATHEXT', '').split(os.pathsep)))
  path = os.environ.get('PATH', None)
  if path is None:
    return []
  for p in os.environ.get('PATH', '').split(os.pathsep):
    p = os.path.join(p, name)
    if os.access(p, flags):
      result.append(p)
    for e in exts:
      pext = p + e
      if os.access(pext, flags):
        result.append(pext)
  return result

# END code by Twisted Matrix Laboratories.

import sys
import subprocess
import glob
import os
import re

def check_dependency() :
  # Check dependency
  if sys.version_info.major < 3 or sys.version_info.minor < 2:
    print("This script requires Python version 3.2.x or above")
    exit(1)
  
  if not which("mkvinfo"):
    print("mkvinfo not found. Please install mkvtoolnix and/or configure PATH variable.")
    exit(1)
  
  if not which("mkvextract"):
    print("mkvextract not found. Please install mkvtoolnix and/or configure PATH variable.")
    exit(1)
  
class State:
  Unknown = -1
  Track = 0
  Attachment = 1
  
class TrackType:
  # Source:
  # mkvtoolnix source code: src/common/matroska.h
  # http://www.matroska.org/technical/specs/codecid/index.html
  Video = 0
  Audio = 1
  Subtitles = 2
  Buttons = 3
  
  DEFAULT_EXT = ""
  
  def __init__(self, arg_codec_id):
    if arg_codec_id is None:
      raise ValueError("Codec ID must not be None")
    elif not isinstance(arg_codec_id, str):
      raise TypeError("Codec ID must be str type. Input type: {0}".format(type(arg_codec_id)))
    
    self.codec_id = arg_codec_id

    if arg_codec_id.startswith("V_"):
      self.type = TrackType.Video
    elif arg_codec_id.startswith("A_"):
      self.type = TrackType.Audio
    elif arg_codec_id.startswith("S_"):
      self.type = TrackType.Subtitles
    elif arg_codec_id.startswith("B_"):
      self.type = TrackType.Buttons
    else:
      raise NotImplementedError("Unimplemeted TrackType")
    
  def __repr__(self):
    return self.codec_id
    
  def ext(self):
    if self.type == TrackType.Video:
      return TrackType.DEFAULT_EXT
    elif self.type == TrackType.Audio:
      return TrackType.DEFAULT_EXT
    elif self.type == TrackType.Subtitles:

      if self.codec_id == "S_TEXT/SSA":
        return ".ssa"
      elif self.codec_id == "S_TEXT/ASS":
        return ".ass"
      elif self.codec_id == "S_TEXT/USF":
        return ".usf"
      elif self.codec_id.startswith("S_VOBSUB"):
        return ".sub"
      elif self.codec_id == "S_TEXT/UTF8" or self.codec_id == "S_TEXT/ASCII":
        return ".srt"
      else:
        raise NotImplementedError("Unknown codec ID: {0}".format(self.codec_id))

    else:
      raise StandardError('Inconsistent internal representation')
      

class Track:
  def __init__(self, arg_num=None, arg_codec_id=None):
    self.num = arg_num
    if arg_codec_id is not None:
      self.type = arg_codec_id
    
  def get_type(self):
    if self._type is not None and not isinstance(self._type, TrackType):
      raise StandardError('Inconsistent internal representation')
    return self._type
    
  def set_type(self, arg_codec_id):
    # NOTE: Does not allow type to be set back to None
    if not isinstance(arg_codec_id, str):
      raise TypeError("Codec ID must be str type. Input type: {0}".format(type(arg_codec_id)))
      
    self._type = TrackType(arg_codec_id)
    
  type = property(get_type, set_type)
    
  def __repr__(self):
    return "Track {0}: {1}".format(self.num, self.type)
    
class Attachment:
  def __init__(self, arg_num, arg_file_name=None):
    if arg_num is None:
      raise ValueError("AID must not be None")
    elif not isinstance(arg_num, int):
      raise TypeError("AID must be int type. Input type: {0}".format(type(arg_num)))
    
    self.aid = arg_num
    
    if arg_file_name is not None:
      self.file_name = arg_file_name
      
  def get_file_name(self):
    return self._file_name
    
  def set_file_name(self, arg_file_name):
    # NOTE: Does not allow file name to be set back to None
    if not isinstance(arg_file_name, str):
      raise TypeError("Filename must be str type. Input type: {0}".format(type(arg_file_name)))
      
    self._file_name = arg_file_name
    
  file_name = property(get_file_name, set_file_name)
    
  def __repr__(self):
    return "Attachment {0}: {1}".format(self.aid, self.file_name)


def get_info(file_path):
  try:
    return subprocess.check_output(["mkvinfo", file_path.input_file_path])
  except subprocess.CalledProcessError as err:
    # print(err.returncode)
    return None

def output_info(file_path, output):
  info_file_path = os.path.join(file_path.output_folder_path, "{0}.info".format(file_path.bare_file_name))
  with open(info_file_path, "wb") as info_file:
    info_file.write(output)

    
def parse_info(file_path, output):
  def get_indent(line):
    return len(line.split("+", 1)[0])
    
  def get_data(line):
    return line.split(":", 1)[1].strip('\r\n\t ')
  
  tracks = []
  attachments = []
  has_chapters = False
  aid = 0
  
  # Parse state
  state = State.Unknown
  # Amount of indentation
  indent = None
  # Temporary object to be filled up with data
  obj = None
  
  # NOTE: The parsing will assume that there are always other entries after "+ Segment tracks" and "+ Attachments"
  for line in output.decode('utf-8').split('\r\n'):
    # print(line)
    
    # Track
    if state == State.Track:
      if get_indent(line) <= indent:
        # print(obj)
        if obj.type.type == TrackType.Subtitles:
          tracks += [obj]
          print("Found subtitle track: {0}".format(obj))
        state = State.Unknown
        obj = None
      elif "+ Track number" in line:
        obj.num = int(get_data(line))
        # print(obj.num)
        # print(line)
      elif "+ Codec ID" in line:
        obj.type = get_data(line)
        # print(obj.type)
        # print(line)
    # Attachment
    elif state == State.Attachment:
      if get_indent(line) <= indent:
        # print(obj)
        attachments += [obj]
        # print("Insert to attachments")
        state = State.Unknown
        obj = None
      elif "+ File name" in line:
        # TODO: What if the file name contains characters not allowed by the platform?
        obj.file_name = get_data(line)
        # print(obj.file_name)
        # print(line)
    
    if "+ A track" in line:
      state = State.Track
      indent = get_indent(line)
      obj = Track()
      # print("Track.__init__")
    elif "+ Attached" in line:
      state = State.Attachment
      indent = get_indent(line)
      aid += 1
      obj = Attachment(arg_num=aid)
      # print("Attachment.__init__: {0}".format(aid))
    elif "+ Chapters" in line:
      has_chapters = True
  
  # print(tracks)
  # print(attachments)
  
  return (tracks, attachments, has_chapters)  
    
def extract_subs(file_path, tracks):
  def subtitle_file_path(file_path, track):
    return os.path.join(file_path.output_folder_path, file_path.bare_file_name + "_" + str(track.num) + track.type.ext())
  
  if not isinstance(file_path, FilePath):
    raise TypeError("FilePath object expected. Input type: {0}".format(type(file_path)))
  if not isinstance(tracks, list):
    raise TypeError("List of tracks expected. Input type: {0}".format(type(tracks)))
  
  if len(tracks) == 0:
    return
  
  args = ["mkvextract", "tracks", file_path.input_file_path];
  
  for track in tracks:
    if not isinstance(track, Track):
      raise TypeError("Track object expected. Input type: {0}".format(type(track)))

    args += ["{0}:{1}".format(track.num, subtitle_file_path(file_path, track))]
  
  subprocess.call(args)
  
def extract_attachments(file_path, attachments):

  if not isinstance(file_path, FilePath):
    raise TypeError("FilePath object expected. Input type: {0}".format(type(file_path)))
  if not isinstance(attachments, list):
    raise TypeError("List of attachments expected. Input type: {0}".format(type(attachments)))
    
  if len(attachments) == 0:
    return
    
  args = ["mkvextract", "attachments", file_path.input_file_path];
    
  for attachment in attachments:
    if not isinstance(attachment, Attachment):
      raise TypeError("Attachment object expected. Input type: {0}".format(type(attachment)))

    args += ["{0}:{1}".format(attachment.aid, os.path.join(file_path.output_folder_path, attachment.file_name))]
    
  subprocess.call(args)
    
    
def extract_chapters(file_path):
  if not isinstance(file_path, FilePath):
    raise TypeError("FilePath object expected. Input type: {0}".format(type(file_path)))
  
  chapter_file_path = os.path.join(file_path.output_folder_path, "{0}_chapters.xml".format(file_path.bare_file_name))
  FOUT = open(chapter_file_path, "w")
  print("Extracting chapters to {0}".format(chapter_file_path).encode(sys.stdout.encoding, 'xmlcharrefreplace'))
  
  subprocess.call(["mkvextract", "chapters", file_path.input_file_path] , stdout=FOUT)

class FilePath:
  def __init__(self, input_file_path):
    if not isinstance(input_file_path, str):
      raise TypeError("str expected for input file path. Input type: {0}".format(type(input_file_path)))

    self.input_file_path = os.path.realpath(input_file_path)

    input_folder_path, input_file_name = os.path.split(self.input_file_path)

    self.bare_file_name = re.sub(r'_', r' ', os.path.splitext(input_file_name)[0])
    self.output_folder_path = os.path.join(input_folder_path, self.bare_file_name)

  def __repr__(self):
    return "Input file: {0}. Output folder: {1}".format(self.input_file_path, self.output_folder_path)
  
  
def extract(file_name):
  file_path = FilePath(file_name)

  print(str(file_path).encode(sys.stdout.encoding, 'xmlcharrefreplace'))

  output = get_info(file_path)

  # If failed to parse the file as MKV
  if output is None:
    return False

  # Create folder with matching name
  os.makedirs(file_path.output_folder_path, exist_ok=True)

  output_info(file_path, output)
    
  tracks, attachments, has_chapters = parse_info(file_path, output)
  
  print(tracks)
  extract_subs(file_path, tracks)
  
  print(attachments)
  extract_attachments(file_path, attachments)
  
  # print(has_chapters)
  if has_chapters:
    extract_chapters(file_path)
  else:
    print("No chapters")
  
  print()
  
  return True

def main():
  check_dependency()
   
  for arg in sys.argv[1:]:
    mkvCount = 0

    try:
      matches = glob.glob(arg)
    
      for filename in matches:
        if extract(filename):
          mkvCount += 1
    except:
      pass
    
    # If no file matches the given pattern, may be the string is not a glob pattern
    # Try to extract the string instead
    if mkvCount == 0:
      extract(arg)

main()
