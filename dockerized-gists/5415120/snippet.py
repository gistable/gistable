import requests
import json

class AbstractDataProvider():
  """A list of methods that data providers should implement or extend."""

  def __init__(self, base_url, username=None, password=None):
    self.base_url = base_url.rstrip('/')
    self.username = username
    self.password = password
        
  def request(self, request_type, path, params=None, data=None, files=None, response_type=None):
    """
    Handles requests for each api call to <api-provider>.
    Since responses are standard from this provider, also return a standard response.
    """
    #if you need to manually set headers or other parameters, set them here
    #example: headers = {'content-type': 'application/json'}
    #you can also dump your data format below under the data arguement. In this example, we're using json.
    url = '{}/{}'.format(self.base_url, path)
    r = requests.request(request_type, url, params=params, data=json.dumps(data), files=files, auth=self.get_credentials(), headers=headers)
  
    if response_type == 'json':
        return r.json()
    else:
        pass

class MyDataProvider(AbstractDataProvider):
  
  def __init__(self, base_url):
    self.base_url = base_url
  
  def get_provider_thingy1(self):
    return self.request('get', 'getproviderthingy1.do', response_type='json')
  
  def get_provider_thingy2(self, myParams):
    return self.request('get', 'getproviderthing2.do', {'myParam': myParam}, response_type='json')

  def post_provider_thingy(self, data):
    return self.request('put', 'postproviderthing.do', data=data)

d = MyDataProvider('http://example.com/')
d.get_provider_thingy2('param')