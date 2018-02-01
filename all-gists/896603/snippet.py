#vim:fileencoding=utf-8
#
# 古いMP3エンコードソフトを使った時、
# ID3タグにSJIS文字列が入っているのを修正する。
#
# エンコーディングがLatin-1なのにSJISらしき物を修正。
#
# 2011-3-31 Shigeru KANEMOTO
# Public Domain
#

import os
import os.path
import eyeD3
import re
import pprint

MUSIC_DIR = '/path/to/your/music/library'
RE_IS_LATIN = re.compile(r'^[\w\s/.!@#$%^&*()-=_+;:\'"[\]?<>,]*$')

w_flag = False
l_flag = False
s_args = []

def fix(fname):
  print fname
  tag = eyeD3.Tag()
  if not tag.link(fname):
    return

  print eyeD3.utils.versionToString(tag.header.version)

  if s_args:
    for s in s_args:
      s = s.split(':', 1)
      print u'Set %s: %s' % tuple(s)
      tag.frames.setTextFrame(str(s[0]), s[1], eyeD3.UTF_16_ENCODING)

  for frame in tag.frames:
    try:
      e = eyeD3.frames.id3EncodingToString(frame.encoding)
      u = frame.text
    except:
      continue
    if not isinstance(u, str) and not isinstance(u, unicode):
      continue

    if l_flag:
      print frame, u, pprint.pformat(u)

    if e == 'latin_1' and not RE_IS_LATIN.match(u):
      u = u.encode('latin_1').decode('shift_jis')
      print 'Recover:', u
      frame.text = u
      frame.encoding = eyeD3.UTF_16_ENCODING

  if w_flag:
    tag.update(eyeD3.ID3_V2_4)
  print

def walk(dirname):
  for dirname, dirs, files in os.walk(dirname):
    for fname in files:
      fix(os.path.join(dirname, fname))

def main():
  global w_flag, l_flag
  import sys
  import getopt

  opts, args = getopt.getopt(sys.argv[1:], 'wls:')
  for opt, arg in opts:
    if opt == '-w':
      w_flag = True
    elif opt == '-l':
      l_flag = True
    elif opt == '-s':
      s_args.append(arg.decode('utf-8'))

  if len(args) == 0:
    walk(MUSIC_DIR)
  else:
    for arg in args:
      if os.path.isdir(arg):
	walk(arg)
      else:
	fix(arg)

if __name__ == '__main__':
  main()
