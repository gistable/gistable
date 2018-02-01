import xml.sax
import xml.sax.handler
import re

class BodyNotFound(Exception):
  pass

class BookHandler(xml.sax.handler.ContentHandler):
  def __init__(self):
    self.inBody = False
    self.text = None

  def startElement(self, name, attr):
    if name == "body":
      if self.text == None:
        self.text = ""
      self.inBody = True

  def characters(self, data):
    if self.inBody:
      self.text += data

  def endElement(self, name):
    if name == "body":
      self.inBody = False

class Fb2Transformer:

  def read(self, filename):
    parser = xml.sax.make_parser()
    handler = BookHandler()
    parser.setContentHandler(handler)
    parser.parse(filename)
    if handler.text == None:
      raise BodyNotFound()
    handler.text = re.sub(r"[^a-zA-Z ]", " ", handler.text)
    handler.text = re.sub(r"[ ]+", " ", handler.text)
    return handler.text.lower()

  def replace(self, filename, dictionary):
    text = open(filename).read()
    for word, trans in dictionary.items():
      nr = "(?i)"+word+"(?![^<]*>)"
      text = re.sub(r""+nr, trans, text)
    return text

