from subprocess import Popen, PIPE, STDOUT, check_output
from mimetools import Message
from StringIO import StringIO
from urlparse import urlparse, parse_qs
from urllib import quote, basejoin, urlencode

DEV_SITE  = 'https://developer.apple.com'
AUTH_SITE = 'https://idmsa.apple.com'
AUTH_PATH = '/IDMSWebAuth/authenticate'
APPIDKEY_PATH = "/services-account/download?path=%s"
DOWNLOAD_PATH = '/devcenter/download.action'
CURL_PATH = '/usr/bin/curl'

PRODUCT_PATH_TEMPLATES = {
    'Xcode': "/Developer_Tools/Xcode_{product[VERSION]}/Xcode_{product[VERSION]}.xip",
}

def product_path_str(prod_name, prod_dict):
    return PRODUCT_PATH_TEMPLATES[prod_name].format(product=prod_dict)

def product_appid_url(prod_name, prod_dict):
    return basejoin(DEV_SITE, APPIDKEY_PATH) % (product_path_str(prod_name, prod_dict))

def product_download_url(prod_name, prod_dict):
    return basejoin(DEV_SITE, ("%s?path=%%s" % DOWNLOAD_PATH) % (product_path_str(prod_name, prod_dict)))

def product_appid(prod_name, prod_dict):
    url = product_appid_url(prod_name, prod_dict)
    raw_response      = check_output([CURL_PATH, '-is', url])
    request, body     = raw_response.split('\r\n\r\n', 1)
    response, headers = request.split('\r\n', 1)
    header_dict       = dict(Message(StringIO(headers)))
    location          = header_dict['location']
    query             = urlparse(location).query
    return parse_qs(query)['appIdKey'][0]

def auth_data(prod_name, prod_dict, appleid, password):
    p1 = "path=%s?%s" % (DOWNLOAD_PATH, quote('path=%s' % product_path_str(prod_name, prod_dict)))
    p2 = urlencode([('appIdKey', product_appid(prod_name, prod_dict))])
    p3 = urlencode([('accNameLocked', 'false')])
    p4 = urlencode([('language', 'US-EN')])
    p5 = urlencode([('Env', 'PROD')])
    p6 = urlencode([('appleId', appleid)])
    p7 = urlencode([('accountPassword', password)])
    data = '&'.join([p1, p2, p3, p4, p5, p6, p7])
    return data

def build_K_file(url, cookies, output=None, headers=True):
    k_file = ""
    k_file += 'url = "%s"\n' % (url)
    if (output is not None):
        k_file += 'output = "%s"\n' % (output)
    k_file += '-s\n'
    if (headers):
        k_file += '-i\n'
    # Now parse cookies
    cookie_body = cookies.split('\n\n',1)[-1]
    cookie_lines = [x.strip() for x in cookie_body.split('\n') if x.strip()]
    k_file += '-b%s' % (';'.join([('='.join([x.split('\t')[-2], x.split('\t')[-1]])) for x in cookie_lines if '_.apple.com\t' in x])) + '\n'
    return k_file

def extract_headers(response, spliton='Location: '):
    header_body = spliton + response.split(spliton, 1)[-1]
    headers     = header_body.split('\r\n\r\n',1)[0]
    return dict(Message(StringIO(headers)))

def extract_cookiejar(response):
    return response.split('\r\n\r\n')[-1]

def first_cookie(header_dict):
    first = header_dict['set-cookie']
    raw_cookie = first.split(';',1)[0]
    # reformat into a 'Netscape-style' cookiejar file with .apple.com as the base
    return '# ignore\n\n#HttpOnly_.apple.com\tTRUE\t/\tTRUE\t0\t' + '\t'.join(raw_cookie.split('=',1)) + '\n'

def download_developer_product(prod_name, prod_dict, appleid, password, output_path, debug=False):
    # Create our authorization POST data body
    authorization_data = auth_data(prod_name, prod_dict, appleid, password)
    # Authorize
    if debug:
        print "* AUTHORIZING ..."
    p = Popen([CURL_PATH, '-is', '-d', '@-', '--cookie-jar', '-', basejoin(AUTH_SITE, AUTH_PATH)], stdout=PIPE, stdin=PIPE, stderr=PIPE)
    result  = p.communicate(input=authorization_data)
    if debug:
        print result
    cookies = extract_cookiejar(result[0])
    # Use the authorization cookies to start the product download, which gives us a 1st redirect
    k_file = build_K_file(product_download_url(prod_name, prod_dict), cookies)
    if debug:
        print "* INITIAL CONNECTION ..."
    p = Popen([CURL_PATH, '-K', '-'], stdout=PIPE, stdin=PIPE, stderr=PIPE)
    result = p.communicate(input=k_file)
    if debug:
        print result
    headers = extract_headers(result[0])
    # Use the output to continue the download, which gives us our 2nd redirect and a new cookie
    new_location = headers['location']
    k_file = build_K_file(new_location, cookies)
    if debug:
        print "* FOLLOW REDIRECT FOR NEW COOKIE ..."
    p = Popen([CURL_PATH, '-K', '-'], stdout=PIPE, stdin=PIPE, stderr=PIPE)
    result = p.communicate(input=k_file)
    if debug:
        print result
    headers = extract_headers(result[0])
    new_location = headers['location']
    # Extract the new cookie
    new_cookies = first_cookie(headers)
    # Now we can really download the file
    k_file = build_K_file(new_location, new_cookies, output=output_path, headers=False)
    if debug:
        print "* STARTING DOWNLOAD!"
    p = Popen([CURL_PATH, '-K', '-'], stdout=PIPE, stdin=PIPE, stderr=PIPE)
    # Get the file!
    result = p.communicate(input=k_file)
    if debug:
        print "* DONE!"
    return result

# Example usage:
# download_developer_product('Xcode', {'VERSION': '8.2.1'}, 'APPLEIDHERE', 'PASSWORDHERE', 'Xcode.xip')
