class FlexibleRequest(urllib2.Request):
  VALID_METHODS = [ 'GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'TRACE', 'OPTIONS', 'CONNECT', 'PATCH' ]
  def __init__(self, *args, **kwargs):
    if 'method' in kwargs:
      if not kwargs['method'] in self.VALID_METHODS:
        raise ValueError("Invalid method specified: %s" % kwargs['method'])
      self.method = kwargs.pop('method')
    else:
      self.method = None
    urllib2.Request.__init__(self, *args, **kwargs)

  def get_method(self):
    if not self.method: return urllib2.Request.get_method(self)
    else: return self.method

## Example:
#req = FlexibleRequest(url, data, method='DELETE')
#response = urllib2.urlopen(req)