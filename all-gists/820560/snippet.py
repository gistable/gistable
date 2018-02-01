class LinkParser(HTMLParser.HTMLParser): 
   def __init__(self, *args, **kargs): 
      HTMLParser.HTMLParser.__init__(self, *args, **kargs)
      self.links = {}
      self.base = None

   def handle_starttag(self, tag, attrs): 
      attrdict = dict(attrs)
      if tag != 'base': 
         self.handle_link(attrdict)
      else: self.base = attrdict.get('href')

   def handle_link(self, attrdict): 
      href = attrdict.get('href')
      src = attrdict.get('src')
      if not (href or src): return

      name = 'href' if href else src
      uri = href if href else src

      uri = urlparse.urldefrag(uri)[0]
      uri = os.path.normpath(uri)
      if self.base is not None: 
         uri = urlparse.urljoin(self.base, uri)
      link = name, uri

      self.links.setdefault(link, [set(), set()])
      rel = attrdict.get('rel', '').strip()
      rev = attrdict.get('rev', '').strip()
      if rel: self.links[link][0] |= set(rel.split(' '))
      if rev: self.links[link][1] |= set(rev.split(' '))
