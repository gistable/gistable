#! /usr/bin/env python
import csv
import urllib2
import sgmllib

class LinkParser(sgmllib.SGMLParser):
  def parse(self, s):
    self.feed(s)
    self.close()

  def __init__(self, verbose=0):
    sgmllib.SGMLParser.__init__(self, verbose)
    self.icons = []
    self.sizes_icon = False
    self.apple_icon = False

  def start_link(self, attribute_tuples):
    # Make a dictionary of attributes for easier look-up.
    attributes = {}
    for name, value in attribute_tuples:
      attributes[name] = value;

    # If we don't have an href, we won't have a useful icon.
    if "href" not in attributes:
      return

    # There can be more than one keyword in the rel attribtue value.
    rel_value = attributes["rel"].split(" ")
    if "icon" in rel_value and "sizes" in attributes:
      print "----- ", attributes["sizes"], attributes["href"]
      self.sizes_icon = True
      self.icons.append({"sizes": attributes["sizes"], "href": attributes["href"]})

    if "apple-touch-icon" in rel_value or "apple-touch-icon-precomposed" in rel_value:
      print "----- apple-touch-icon", attributes["href"]
      self.apple_icon = True
      self.icons.append({"apple-touch-icon": "true", "href": attributes["href"]})

  def get_icons(self):
    return self.icons

  def has_sizes_icon(self):
    return self.sizes_icon

  def has_apple_icon(self):
    return self.apple_icon

# site_url: [{ "sizes": sizes, "href": href }, ... ]
sites_to_icons = {}
sizes_icon_count = 0
apple_icon_count = 0
url_count = 0

# urls.csv is a comma-separated list on urls on a single row
reader = csv.reader(open('urls.csv', 'rb'))
urls = reader.next()

opener = urllib2.build_opener()
# Un-comment this line to test with an iPhone user agent
# opener.addheaders = [("User-agent", "Apple-iPhone3C1/801.306")]

for url in urls:
  print "fetching", url
  try:
    f = opener.open(url)
    s = f.read()
    f.close()
  except:
    print "ERROR fetching", url

  print "parsing", url
  parser = LinkParser()
  try:
    parser.parse(s)
  except:
    print "ERROR parsing", url

  sites_to_icons[url] = parser.get_icons()
  if parser.has_sizes_icon():
    sizes_icon_count = sizes_icon_count + 1
  if parser.has_apple_icon():
    apple_icon_count = apple_icon_count + 1
  url_count = url_count + 1

  print "sizes_icon_count =", sizes_icon_count, "apple_icon_count =", apple_icon_count, "url_count=", url_count

print sites_to_icons
