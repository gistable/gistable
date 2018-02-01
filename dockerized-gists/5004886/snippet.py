# -*- coding: utf-8 -*-
"""
    bugsense_cli.py
    ~~~~

    Sample script to upload dSYMSs and access the Read API
    :version: 0.1
    :copyright: 2013 by bugsense.com.
"""
from urllib import quote
import argparse
import requests
import zipfile
import json
import os

base = 'https://www.bugsense.appspot.com'
#base = 'http://localhost:8080'

# add args for file, apikey
def upload_dsym(api_key, token, filename):
    url = lambda  x: "%s/api/v1/project/%s/dsym.json"%(base, x) #https://www.bugsense.com
    def zipdir(basedir, zf):
        from contextlib import closing
        assert os.path.isdir(basedir)
        with closing(zf) as z:
            for root, dirs, files in os.walk(basedir):
                #NOTE: ignore empty directories
                for fn in files:
                    absfn = os.path.join(root, fn)
                    zfn = absfn[len(basedir)+len(os.sep):] #XXX: relative path
                    z.write(absfn, zfn)

    headers = {'X-BugSense-Auth-Token': token}
    files = { 'file': None }
    # If zip then upload
    if zipfile.is_zipfile(filename):
        files['file'] = open( filename, 'rb')
    # If file is not zip it should zip it
    elif os.path.isdir(filename):
        import StringIO
        o = StringIO.StringIO()
        zf = zipfile.ZipFile(o, mode='w')
        zipdir(filename, zf)
        zf.close()
        o.seek(0)
        files['file'] = o.read()
        o.close()

    resp = requests.post(url(api_key), files=files, headers=headers, verify=False)

    return resp.text


# add args for file, apikey
def upload_mappings(api_key, token, filename, app_version):
    url = lambda  x: "%s/api/v1/project/%s/mappings.json"%(base, x)

    headers = {'X-BugSense-Auth-Token': token}
    files = { 'file': open(filename, 'rb') }

    resp = requests.post(url(api_key), 
    					 params={'app_version': app_version}, 
						 files=files, 
						 headers=headers, 
						 verify=False)

    return resp.text
    

def get_errors(api_key, token,
               days=7, 
               status='open', 
               page=0, 
               app_version=None, 
               os_version=None, 
               tag=None, 
               search=None,
               order=None):
    """ 
    Get errors 
    Alternatively with cURL:
    curl --header "X-BugSense-Auth-Token: YOUR_API_TOKEN"  https://www.bugsense.com/api/v1/project/YOUR_API_KEY/errors.json
    """
    url = lambda  x: "%s/api/v1/project/%s/errors.json"%(base, x) #https://www.bugsense.com
    headers = {'X-BugSense-Auth-Token': token}
    params = {
        'days': days,
        'status': 'new' if status=='open' else 'resolved',
        'page': page,
        'appver': app_version,
        'osver': os_version,
        'tag': tag,
        'message': search,
        'order': order
    }
    params_str =  ('&').join([k+'='+quote(v) for k,v in params.items() if v])
    
    resp = requests.get(url(api_key)+'?'+params_str, headers=headers)

    return resp.text

def get_error(api_key, token, eid, logs=False):
    """ Get error details """
    url = "%s/api/v1/project/%s/error/%s.json"%(base, api_key, eid) #https://www.bugsense.com
    headers = {'X-BugSense-Auth-Token': token}
    resp = requests.get(url, headers=headers)

    return resp.text


def get_insights(api_key, token, insights, **kwargs):
    """ 
    Get Insights Boxes information 
    Alternatively with cURL:
    curl --header "X-BugSense-Auth-Token: 9eca658329024b1b477053c"  https://www.bugsense.com/api/v1/project/7efxxd27/analytics.json
    """
    base_url = "%s/api/v1/project/%s/"%(base, api_key) #https://www.bugsense.com
    urls = {
        'users': 'analytics.json?category=users',
        'sessions': 'analytics.json?category=sessions',
        'devices': 'analytics/devices.json',
        'app_versions': 'analytics/versions.json?category=app_versions',
        'os_versions': 'analytics/versions.json?category=os_versions',
        'top_errors': 'analytics/top_errors.json',
        'trending_errors': 'analytics/trending_errors.json'  
    }
    if insights in urls:
        base_url += urls[insights]
    else:
        base_url += "%s.json"%(insights)

    headers = {'X-BugSense-Auth-Token': token}
    resp = requests.get(base_url, headers=headers)

    return resp.text


if __name__ == '__main__':
    """
    Examples:
    >>> python bugsense_cli.py 8efxxd27 8eca658329099b1b38905ca -days 20
    >>> python bugsense_cli.py 8efxxd27 8eca658329099b1b38905ca -insights trending_errors
    >>> python bugsense_cli.py 8efxxd27 8eca658329099b1b38905ca -dsym ../dsyms/crash-me3.app.dSYM
    >>> python bugsense_cli.py 8efxxd27 8eca658329099b1b38905ca -mappings mappings.txt
    """
    
    parser = argparse.ArgumentParser(description='BugSense CLI client.')
    parser.add_argument('api', help='Application API Key ex. f2gx13')
    parser.add_argument('token', help='Auth Token ')
    parser.add_argument('-id',  help='Get error by id')
    parser.add_argument('-resolve',  help='resolve 23 to resolve error 23')
    parser.add_argument('-dsym', help='dSYM file name ex. myApp.dsym')
    parser.add_argument('-mappings', help='Proguard mappings file name ex. mappings.txt')
    parser.add_argument('-days', help='Show errors of last n days')
    parser.add_argument('-status', help='Get errors that either open|resolved', default='open')
    parser.add_argument('-page', help='Get errors page', default=0)
    parser.add_argument('-app_version', help='Get errors for app version', default=None)
    parser.add_argument('-os_version', help='Get errors for os version', default=None)
    parser.add_argument('-tag', help='Get errors for tag', default=None)
    parser.add_argument('-search', help='Get errors by error messsage or custom ex. key1:val1', default=None)
    parser.add_argument('-order', help='Order errors by created|updated|total|appversion')
    parser.add_argument('-insights', help='Choose insight users|sessions|app_versions|os_versions|devices|top_errors|trending_errors')
    
    args = parser.parse_args()

    response = '{}'

    if args.dsym:
        response = upload_dsym(args.api, args.token, args.dsym)
    elif args.mappings:
        response = upload_mappings(args.api, args.token, args.mappings, args.app_version)
    elif args.insights:
        response = get_insights(args.api, args.token, args.insights)
    elif args.id:
        response = get_error(args.api, args.token, args.id)
    elif args.days or args.search or args.app_version or args.status:
        response = get_errors(args.api, args.token, 
                              days=args.days, 
                              status=args.status, 
                              page=args.page,
                              app_version=args.app_version, 
                              os_version=args.os_version,
                              tag=args.tag,
                              search=args.search)

    # You can print, store, process, etc the results
    print json.loads(response)