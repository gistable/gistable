import sys
import argparse
import os
import sqlite3

import apiclient.discovery
import httplib2
import uritemplate
from oauth2client.anyjson import simplejson
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
import oauth2client.tools

def buildDiscoveryObject(api, api_ver):
  params = {
      'api': api,
      'apiVersion': api_ver
      }
  http = httplib2.Http()
  requested_url = uritemplate.expand(apiclient.discovery.DISCOVERY_URI, params)
  resp, content = http.request(requested_url)
  if resp.status == 404:
    raise UnknownApiNameOrVersion("name: %s  version: %s" % (main_options.api, main_options.api_ver))
  if resp.status >= 400:
    raise HttpError(resp, content, uri=requested_url)
  try:
    return simplejson.loads(content)
  except ValueError, e:
    logger.error('Failed to parse as JSON: ' + content)
    raise InvalidJsonError()

def buildHttpObject(method_object, api=None, api_ver=None):
  if 'scopes' in method_object:
    possible_scopes = method_object['scopes']
    CLIENT_SECRETS = os.path.join(module_path(), 'client_secrets.json')
    # Helpful message to display in the browser if the CLIENT_SECRETS file
    # is missing.
    MISSING_CLIENT_SECRETS_MESSAGE = """
  WARNING: Please configure OAuth 2.0

  To make this sample run you will need to populate the client_secrets.json file
  found at:

   %s

  with information from the APIs Console <https://code.google.com/apis/console>.

  """ % CLIENT_SECRETS

    # Set up a Flow object to be used if we need to authenticate.
    FLOW = flow_from_clientsecrets(CLIENT_SECRETS,
      scope=possible_scopes,
      message=MISSING_CLIENT_SECRETS_MESSAGE)
    sqldbfile = os.path.join(module_path(), 'oauth.db')
    newDB = (not os.path.isfile(sqldbfile))
    sqlconn = sqlite3.connect(sqldbfile, detect_types=sqlite3.PARSE_DECLTYPES)
    sqlconn.text_factory = str
    sqlcur = sqlconn.cursor()
    if newDB:
      sqlcur.executescript('''CREATE TABLE oauthfiles(
                                scope TEXT PRIMARY KEY, 
                                file TEXT);''')
      sqlconn.commit()
    oauthfile = None
    for scope in possible_scopes:
      scope_query = sqlcur.execute('SELECT file FROM oauthfiles WHERE scope = ?', (scope,))
      scope_results = sqlcur.fetchall()
      if len(scope_results) > 0:
        oauthfile = scope_results[0][0]
        break
    if oauthfile == None:
      oauthfile = possible_scopes[0].lower()
      oauthfile = oauthfile.replace(u'https://', u'')
      oauthfile = oauthfile.replace(u'http://', u'')
      oauthfile = oauthfile.replace(u'/', u'_')
      oauthfile = u'oauth_%s' % oauthfile
    oauth_fullpath = os.path.join(module_path(), oauthfile)
    storage = Storage(oauth_fullpath)
    credentials = storage.get()
    http = httplib2.Http()
    if credentials is None or credentials.invalid:
      flags = cmd_flags()
      if os.path.isfile(os.path.join(module_path(), 'nobrowser.txt')):
        flags.noauth_local_webserver = True
      credentials = oauth2client.tools.run_flow(FLOW, storage, flags, http=http)
      for scope in possible_scopes:
        sqlcur.execute('INSERT INTO oauthfiles (scope, file) VALUES (?, ?)', (scope, oauthfile))
      sqlconn.commit()
    http = credentials.authorize(http)
  else:
    http = httplib2.Http()
  return http

def showPossibleAPIs():
  discovery_object = buildDiscoveryObject('discovery', 'v1')
  http = buildHttpObject(discovery_object)
  service = apiclient.discovery.build('discovery', 'v1', http=http)
  try:
   result = service.apis().list().execute()
  except apiclient.errors.HttpError, e:
    print e.resp['status'], simplejson.loads(e.content)['error']['message']
    return
  print '--api and --api_ver are required parameters. Possible values are:\n'
  for api in result['items']:
    if api['preferred'] == True or api['version'][0] != 'v':
      print ' --api %s --api_ver %s' % (api['name'], api['version'])
 
def parseMainArgs(argv):
  parser = argparse.ArgumentParser()
  parser.add_argument('--api', help='Google API to act against.')
  parser.add_argument('--api_ver', help='Version of Google API to use')
  parser.add_argument('--resource', help='Resource to act against.')
  parser.add_argument('--method', help='Method to perform.')
  parser.add_argument('--media_body', help='File to upload as media body.')
  parser.add_argument('--debug', action='store_true', help='Show HTTP Debug output.')
  return parser.parse_known_args(sys.argv)

def parseUrlArgs(method_object, argv):
  parser = argparse.ArgumentParser()
  parser.add_argument('--fields', help='ask the server to send only the fields you need.')
#  parser.add_argument('--callback', help='Name of the JavaScript callback function that handles the response.')
  parser.add_argument('--prettyPrint', action='store_true', help='Returns the response in a human-readable format.')
  parser.add_argument('--quotaUser', help='Lets you enforce per-user quotas from a server-side application even in cases when the user\'s IP address is unknown. (Defaults to true)')
  parser.add_argument('--userIp', help='IP address of the end user for whom the API call is being made.')
  if 'parameters' in method_object:
    for parameter in method_object['parameters']:
      parser.add_argument('--%s' % parameter)
  return parser.parse_known_args(argv)

def parseBodyArgs(json_service, method_object, argv):
  if 'request' in method_object:
    body_args = argparse.ArgumentParser()
    body_resource = method_object['request']['$ref']
    for body_param in json_service['schemas'][body_resource]['properties']:
      if body_param in ['kind', 'etag']:
        continue
      if ('description' in json_service['schemas'][body_resource]['properties'][body_param]) and json_service['schemas'][body_resource]['properties'][body_param]['description'][-11:] == '(Read-only)':
        continue
      body_args.add_argument('--%s' % body_param, default='')
    return vars(body_args.parse_args(argv))
  else:
    return None

def we_are_frozen():
  """Returns whether we are frozen via py2exe.
  This will affect how we find out where we are located."""

  return hasattr(sys, "frozen")

def module_path():
  """ This will get us the program's directory,
  even if we are frozen using py2exe"""

  if we_are_frozen():
    return os.path.dirname(unicode(sys.executable, sys.getfilesystemencoding( )))
  return os.path.dirname(unicode(__file__, sys.getfilesystemencoding( )))

class cmd_flags(object):
  def __init__(self):
    self.short_url = False
    self.noauth_local_webserver = False
    self.logging_level = 'ERROR'
    self.auth_host_name = 'localhost'
    self.auth_host_port = [8080, 9090]

def main(argv):
  main_options, leftover_options = parseMainArgs(argv)
  if main_options.debug:
    httplib2.debuglevel = 4
  if main_options.api == None or main_options.api_ver == None:
    showPossibleAPIs()
    return
  discovery_object = buildDiscoveryObject(main_options.api, main_options.api_ver)
  try:
    split_resource = main_options.resource.split(u'.')
    resource_object = discovery_object
    for an_object in split_resource:
      resource_object = resource_object[u'resources'][an_object]
  except (KeyError, AttributeError):
    if main_options.resource == None:
      print 'ERROR: need to specify --resource <resource>. Possible resources are:'
    else:
      print 'ERROR: %s is not a valid resource. Possible resources are:' % main_options.resource
    for resource in discovery_object['resources']:
      if u'methods' in discovery_object[u'resources'][resource]:
        print u' %s' % resource
      elif u'resources' in discovery_object[u'resources'][resource]:
        for subresource in discovery_object[u'resources'][resource][u'resources']:
          print u' %s.%s' % (resource, subresource)
    return
  try:
    method_object = resource_object['methods'][main_options.method]
  except KeyError:
    if main_options.method == None:
      print 'ERROR: need to specify --method <method>. Possible methods are:'
    else:
      print 'ERROR: %s is not a valid method. Possible methods are:' % main_options.method
    for method in resource_object['methods']:
      print method
    return
  http = buildHttpObject(method_object, main_options.api, main_options.api_ver)
  service = apiclient.discovery.build(main_options.api, main_options.api_ver, http=http)
  resource_to_call = service
  for a_resource in split_resource:
    try:
      resource_to_call = getattr(resource_to_call, a_resource)
    except AttributeError:
      resource_to_call = getattr(resource_to_call(), a_resource)
  method_to_call = getattr(resource_to_call(), main_options.method)
  url_options, still_leftover_options = parseUrlArgs(method_object=method_object, argv=leftover_options[1:])
  body = parseBodyArgs(discovery_object, method_object, still_leftover_options)
  if body:
    url_options.body = {}
    for key in body.keys():
      if body[key] not in [None, u'']:
        url_options.body[key] = body[key]
  if main_options.media_body:
    url_options.media_body = main_options.media_body
  try:
    result = method_to_call(**vars(url_options)).execute()
  except apiclient.errors.HttpError, e:
    print e.resp['status'], simplejson.loads(e.content)['error']['message']
    return
  except TypeError, e:
    print e
    return
  if url_options.fields:
    print result[url_options.fields]
  else:
    print simplejson.dumps(result, sort_keys=True, indent=2, separators=(',', ': '))

if __name__ == '__main__':
  main(sys.argv)