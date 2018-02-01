#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
@ Autor:     [[Usuário:Danilo.mac]]

@ Licença:   GNU General Public License 3.0 (GPL V3) e Creative Commons Attribution/Share-Alike (CC-BY-SA)

Descrição:   Script para busca de referencias no dump dos históricos da Wikipédia lusófona.

"""
import bz2, re, os, codecs, socket, time

namespaces = ('0', '102')
reTag = re.compile(ur'(?s)<(ns|id|timestamp|text)[^<>]*>([^<]*)</\1>')
ddir = '/public/dumps/public/ptwiki/' + max(os.listdir('/public/dumps/public/ptwiki/'))
print ddir
dumps = [ddir + '/' + [a for a in os.listdir(ddir) if a.endswith('-pages-meta-history{}.xml.bz2'.format(n))][0] for n in (1, 2, 3, 4)]

start = int(time.time())
def runtime():
  t = int(time.time()) - start
  return (t > 3600 and '{}h '.format(t / 3600) or '') + ('{}min '.format(t % 3600 / 60)) + ('{}s'.format(t % 60))

class Page(object):
  reRef = re.compile(r'&lt;ref ?(?:name=(?:&quot;|&apos;)?([^&]+))?')

  def __init__(self, id):
    self.id = id
    self.data = []

  def revision(self, month, text):
    ref = len(set(r or n for n, r in enumerate(self.reRef.findall(text))))
    http = text.find('http://') != -1 or text.find('https://') != -1
    section = text.find('{{referências}}') != -1 or text.find('{{Referências}}') != -1
    if not self.data:
      self.data.append([month, (http, section, ref)])
    elif self.data[-1][1] != (http, section, ref):
      if self.data[-1][0] == month:
        self.data[-1][1] == (http, section, ref)
      else:
        self.data.append([month, (http, section, ref)])

  def get(self):
    data = ['{}{}{}{}'.format(month, int(data[0]), int(data[1]), data[2]) for month, data in self.data]
    return '{} {}'.format(self.id, ','.join(data))

def gen(dumps):
  buf = bytearray()
  for dump in dumps:
    f = bz2.BZ2File(dump)
    buf.extend(f.read(10000000))
    while True:
      for tag in reTag.finditer(buf):
        yield tag
      del buf[0:tag.end()]
      l = len(buf)
      buf.extend(f.read(10000000))
      if len(buf) == l:
        break
    f.close()
    print dump, runtime()

def main(f=None):
  c, p = 0, 0
  pagens = False
  page = None
  month = None
  for tag in gen(dumps):
    if tag.group(1) == 'ns':
      if page:
        f.write(page.get() + '\n')
      if str(tag.group(2)) in namespaces:
        pagens = True
      page = None
    elif pagens and tag.group(1) == 'id':
      pagens = False
      page = Page(int(tag.group(2)))
      p += 1
    elif page:
      if tag.group(1) == 'timestamp':
        month = tag.group(2)[2:4] + tag.group(2)[5:7]
      elif tag.group(1) == 'text':
        c += 1
        page.revision(month, str(tag.group(2)))

  # Sends a message to #wikipedia-pt-tecn in Freenode when the job is concluded
  wmbot(u'danilo: Busca no dump concluída: {} páginas, {} revisões em {}'.format(p, c, runtime()))

def wmbot(message):
  if not isinstance(message, basestring):
    print 'Erro em wmbot({!r})'.format(message)
    return
  if isinstance(message, unicode):
    message = message.encode('utf-8')
  s = socket.socket()
  s.connect(('wm-bot.eqiad.wmflabs', 64834))
  s.send('#wikipedia-pt-tecn ' + message)
  s.shutdown(socket.SHUT_RDWR)

if __name__ == "__main__":
  with open('refs.txt', 'w') as f:
    main(f)