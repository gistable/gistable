'''
NOTES:

 - See the ArcGIS REST API documentation for supported operations, methods, and syntax:
        http://resources.arcgis.com/en/help/arcgis-rest-api/
 - A TOKEN must be passed as parameter in addition to any required inputs for the operation.
 - "urllib.urlencode" handles spaces and other special characters in parameters so that valid URLs are constructed.
 - "urllib.urlopen" sends the reqest and handles the response.
 - Parameters are appended to URL for GET (see Example 1), but passed to "urlopen" for POST (see Example 2).  API docs specifiy supported methods for each operation.
 - "json.loads" converts string responses to parseable JSON objects.
 - Labels in << >> are placeholders and would be replaced with objects in your code.
     - <<portal>> = 'https://arcgis.com' for ArcGIS Online organizations, or URL to your Portal for ArcGIS web adaptor
 '''

import urllib, json

# replace <<PLACEHOLDERS>> in next three lines with your information
# e.g., portal = 'https://www.arcgis.com', username = 'jdoe1234', password = 'mypassword'
portal = '<<PORTAL>>'
username = '<<USERNAME>>'
password = '<<PASSWORD>>'

# Generate Token Example
parameters = urllib.urlencode({'username':username,'password':password,'client':'requestip','f':'json'})
request = portal + '/sharing/rest/generateToken?'
response = json.loads(urllib.urlopen(request, parameters).read())

token = response['token']

# EXAMPLE1: request user content (GET method)
parameters1 = urllib.urlencode({'token': token, 'f': 'json'})
request1 = portal + '/sharing/rest/content/users/' + username + '?' + parameters   # params appended to URL for GET
response1 = json.loads(urllib.urlopen(request).read())

# EXAMPLE2: create folder in My Content (requires POST method)
parameters2 = urllib.urlencode({'title' : <<title>>, 'token': token, 'f': 'json'})
request2 = portal + '/sharing/rest/content/users/' + username + '/createFolder?'           
response2 = json.loads(urllib.urlopen(request2, parameters2).read())   # params passed to urlopen for POST