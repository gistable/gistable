"""
This example requires the body-streaming tornado fork at https://github.com/nephics/tornado.
Refer to http://groups.google.com/group/python-tornado/browse_thread/thread/791c67cb86c2dea2.

Supports uploading an unlimited number/size of files in a single
PUT multipart/form-data request. Each file is processed as the stream
finds the part in the form data.

==USAGE==

After starting this test tornado instance using the fork
at https://github.com/nephics/tornado, this can be tested
using the curl command:

curl -X PUT -F file=@/path/to/file#1 -F file=@/path/to/file#2 http://localhost:8888
"""

import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.httputil
import tornado.escape
import tempfile
import cgi

@tornado.web.stream_body
class MultipartFormdataHandler(tornado.web.RequestHandler):
  """Process a multipart/form-data data stream"""

  # flag to only accept form parts with file data (has a filename)
  files_only = True

  def initialize(self):
    # currently processing form part
    self.current_part = None
    # bytes left to process in the stream
    self.bytes_left = int(self.request.headers.get("Content-Length", 0))
    # buffer needed to accurately identify form data parts
    self._buffer = ""

    # requires multipart/form-data content
    content_type = self.request.headers.get("Content-Type", "")
    if not self.bytes_left or not content_type.startswith("multipart"):
      raise tornado.web.HTTPError(405)

    # extract the multipart boundary
    fields = content_type.split(";")
    for field in fields:
      k, sep, v = field.strip().partition("=")
      if k == "boundary" and v:
        if v.startswith(b'"') and v.endswith(b'"'):
          self.boundary = tornado.escape.utf8(v[1:-1])
        else:
          self.boundary = tornado.escape.utf8(v)
        break
    else:
      raise tornado.httpserver._BadRequestException("Invalid multipart/form-data")

  def put(self):
    # directory to put uploaded files to
    self.tmpdir = tempfile.mkdtemp(prefix="multipart-uploads-")
    # setup callbacks for each part of the multiform data
    self.onpart = lambda filename, header: open("%s/%s" % (self.tmpdir, filename), "w")
    self.ondata = lambda file, chunk: file.write(chunk)
    self.onclose = lambda file: (file.close(), self.write("Finished upload of %s" % file.name), self.flush())
    self.onfinish = lambda: self.finish()
    # initialize streaming
    self.stream_data()
  
  def onpart(self, name, content_type):
    raise NotImplementedError("Required onpart callback")
  
  def ondata(self, part, data):
    raise NotImplementedError("Required ondata callback")
  
  def onclose(self, part):
    raise NotImplementedError("Required onclose callback")
  
  def onfinish(self):
    raise NotImplementedError("Required onfinish callback")
  
  def stream_data(self):
    # don't like needing to access the iostream private read_buffer_size variable
    # but it is needed to ensure we always consume as much as is available to avoid
    # overflowing the max read buffer size on large uploads
    self.request.connection.stream.read_bytes(min(self.bytes_left, max(4096, self.request.connection.stream._read_buffer_size)), self._stream)

  def close(self):
    if self.current_part:
      self.onerror(self.current_part)

  def _stream(self, data):
    self.bytes_left -= len(data)
    data = self._buffer + data
    delimiter = data.find(b"--%s" % self.boundary)
    delimiter_len = len(b"--%s" % self.boundary)
    eoh = None
    if delimiter != -1:
      data, self._buffer = data[0:delimiter], data[delimiter:]
      eoh = self._buffer.find("\r\n\r\n")
    
    else:
      # leave the end of the chunk so the boundary does not get lost if
      # it cutoff part-way
      endlen = len(self.boundary) + 4
      data, self._buffer = data[0:-endlen], data[-endlen:]
    
    # stream data to part handler
    if data:
      if self.current_part:
        self.ondata(self.current_part, data)
    
    # move on to the next part (or start) if we have a header in the buffer
    if eoh >= 0:
      self._header(self._buffer[delimiter_len+2:eoh])
      self._buffer = self._buffer[eoh+4:]
    
    # check if the stream finished
    if delimiter != -1 and self._buffer[delimiter_len:delimiter_len+2] == "--":
      if self.current_part:
        self.onclose(self.current_part)
        self.current_part = None
      return self.onfinish()
    
    # continue streaming 
    self.stream_data()

  def _header(self, header):
    # close any open parts as they are done
    if self.current_part:
      self.onclose(self.current_part)
      self.current_part = None
    
    header_check = header.find(self.boundary)
    if header_check != -1:
      logging.warning("multipart/form-data missing headers")
      header = header[header_check:]
    # convert to dict
    header = tornado.httputil.HTTPHeaders.parse(header.decode("utf-8"))
    disp_header = header.get("Content-Disposition", "")
    disposition, disp_params = tornado.httputil._parse_header(disp_header)
    next = False
    if disposition != "form-data":
      logging.warning("Invalid multipart/form-data")
      return
    if not disp_params.get("name"):
      logging.warning("multipart/form-data value missing name")
      return

    if self.files_only and "filename" not in disp_params:
      # this part is invalid, move on to the next one
      logging.warning("multipart/form-data part missing required file data")
      return

    # stream files non-blocking to the handler one file at a time
    else:
      self.current_part = self.onpart(disp_params["filename"] if self.files_only else disp_params["name"], header.get("Content-Type", "application/unknown"))

application = tornado.web.Application([
    (r"/", MultipartFormdataHandler),
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
