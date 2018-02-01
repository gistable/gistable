import urllib3
from urlparse import urlparse
import os
import json
from urllib import urlencode
from time import sleep
import pprint
import argparse
import sys

http = urllib3.PoolManager()

def gen_headers(domain, app_token, username, password):
    headers = urllib3.util.make_headers(basic_auth='{username}:{password}'.format(
        username = username,
        password = password
    ))
    headers.update({
        'X-App-Token': app_token,
        'X-Socrata.Host': urlparse(domain).netloc,
        'Content-Type': 'application/octet-stream'
    })
    return headers

def print_response(tag, response):
    print("{tag} returned with {status}".format(
            tag = tag,
            status = response.status
        ))
    if response.status > 300:
        print(response.data)

def scan(filename, domain, app_token, username, password):
    print("Starting scanShape for {filename}".format(filename = filename))

    headers = gen_headers(domain, app_token, username, password)
    headers['X-File-Name'] = os.path.basename(filename)

    with open(filename) as payload:
        response = http.urlopen(
            'POST',
            '{domain}/imports2?method=scanShape&fileUploaderfile={filename}'.format(
                domain = domain,
                filename = filename
            ),
            headers = headers,
            body = payload
        )

        print_response("Scan file", response)
        return response.status, json.loads(response.data)

def create(domain, app_token, username, password, name, file_id):
    headers = gen_headers(domain, app_token, username, password)
    headers['Content-Type'] = 'application/x-www-form-urlencoded'

    response = http.urlopen(
        'POST',
        '{domain}/imports2?method=shapefile'.format(
            domain = domain
        ),
        headers = headers,
        body = urlencode({
            'name': name,
            'fileId': file_id,
            'blueprint': {'layers': []}
        })
    )

    print_response("Create Import", response)
    return response.status, json.loads(response.data)

def replace(domain, app_token, username, password, name, file_id, replace_into):
    headers = gen_headers(domain, app_token, username, password)
    headers['Content-Type'] = 'application/x-www-form-urlencoded'

    response = http.urlopen(
        'POST',
        '{domain}/imports2?method=replaceShapefile'.format(
            domain = domain
        ),
        headers = headers,
        body = urlencode({
            'name': name,
            'fileId': file_id,
            'viewUid': replace_into,
            'blueprint': {'layers': []}
        })
    )

    print_response("Replace File", response)
    return response.status, json.loads(response.data)

def poll(domain, app_token, username, password, ticket):
    headers = gen_headers(domain, app_token, username, password)

    response = http.request(
        'GET',
        '{domain}/imports2?method=shapefile&ticket={ticket}'.format(
            domain = domain,
            ticket = ticket
        ),
        headers = headers
    )
    data = json.loads(response.data)

    if data.get('code', 'accepted'):
        details = data.get('details', {})
        status = details.get('status', False) or details.get('stage', '??')
        progress = details.get('progress', 0)
        print("Import in progress, {progress} status: {status}".format(
            status = status,
            progress = progress
        ))

    return response.status, json.loads(response.data)

def run_import(create_or_replace, filename, domain, app_token, username, password):
    scan_status, scan_response = scan(
        filename,
        domain,
        app_token,
        username,
        password
    )
    if scan_status == 200:
        create_status, create_response = create_or_replace(scan_response['fileId'])
        ticket = create_response.get('ticket', False)

        if not ticket:
            return False, {
                'step': 'submit',
                'status': create_status,
                'response': create_response
            }

        while ticket:
            poll_status, wait_or_view = poll(domain, app_token, username, password, ticket)
            ticket = wait_or_view.get('ticket', False)

            if poll_status == 200:
                return True, wait_or_view

            sleep(2)

        return False, {
            'step': 'poll',
            'status': poll_status,
            'response': wait_or_view
        }

    else:
        return False, {
            'step': 'scan',
            'status': status,
            'response': response
        }

def create_shape(filename, domain, app_token, username, password):
    importer = lambda file_id: create(
        domain, app_token, username, password, filename, file_id
    )
    return run_import(importer, filename, domain, app_token, username, password)

def replace_shape(filename, replaceInto, domain, app_token, username, password):
    importer = lambda file_id: replace(
        domain, app_token, username, password, filename, file_id, replaceInto
    )
    return run_import(importer, filename, domain, app_token, username, password)


def main():

    parser = argparse.ArgumentParser(description='Import via imports2')

    parser.add_argument(
        'operation',
        help = 'The operation you want',
        choices = ['create', 'replace'],
        type = str
    )

    parser.add_argument(
        'filename',
        help = 'The file you want to import',
        type = str
    )
    parser.add_argument(
        'domain',
        help = 'The domain you are importing to',
        type = str
    )
    parser.add_argument(
        '--app_token',
        help='Your app token',
        type=str,
        default = os.environ['SOCRATA_APP_TOKEN'],
        action = 'store'
    )
    parser.add_argument(
        '--username',
        help = 'Your username',
        type = str,
        default = os.environ['SOCRATA_USER'],
        action = 'store'
    )
    parser.add_argument(
        '--password',
        help = 'Your password',
        type = str,
        default = os.environ['SOCRATA_PASS'],
        action = 'store'
    )
    parser.add_argument(
        '--replace-view',
        help = 'The view you want to replace',
        type = str,
        action = 'store'
    )

    args = parser.parse_args()

    success, view_or_error = False, False
    if args.operation == 'create':
        success, view_or_error = create_shape(
            args.filename,
            args.domain,
            args.app_token,
            args.username,
            args.password
        )
    elif args.operation == 'replace':
        if not args.replace_view:
            print("Replace must provide a --replace-view option")
            return sys.exit(1)
        success, view_or_error = replace_shape(
            args.filename,
            args.replace_view,
            args.domain,
            args.app_token,
            args.username,
            args.password
        )

    pp = pprint.PrettyPrinter(indent = 4)
    if success:
        print("Created view")
        pp.pprint(view_or_error)
        sys.exit(0)
    else:
        print("Failed to create the view")
        pp.pprint(view_or_error)
        sys.exit(1)

if __name__ == '__main__':
  main()