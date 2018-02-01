#!/usr/bin/env python

"""
Tool to download conference information from Indico
"""

import json, argparse, sys, re, logging, os, importlib

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s: %(message)s')

for module in ('unidecode', 'requests'):
    try:
        locals()[module] = importlib.import_module(module)
    except ImportError:
        logger.critical('You need to download the {} Python package to use this tool.'.format(module))
        sys.exit(1)

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('resource', metavar='URL_OR_FILE', help='HTTP URL or local json file')
parser.add_argument('--output-folder', '-o', default='./', help='Folder to store the output in. Default: current working directory')
parser.add_argument('--interactive', '-i', help='Enable an interactive mode before downloading files.')
args = parser.parse_args()

if args.interactive:
    try:
        import IPython
    except ImportError:
        parser.error('Need to install IPython to use --interactive mode')


if re.match(r'^https?://', args.resource):
    params = {
      'occ':      'yes',
      'pretty':   'yes',
      'detail': 'contributions',
    }
    try:
        r = requests.get(args.resource, params=params)
    except (requests.exceptions.InvalidURL, requests.exceptions.ConnectionError) as e:
        msg = 'Could not fetch the URL'
        try:
            msg += ': ' + str(e.args[0].args[0])
        except: pass
        logger.critical(msg)
        sys.exit(2)
    #: jr = json response
    jr = json.loads(r.text)
else:
    with open(args.resource, 'r') as d:
        jr = json.loads(d.read())

assert 'count' in jr
assert jr['count'] == 1
cs = jr['results'][0]['contributions'] # contributions
cs.sort(key=lambda c: int(c['id']))

if args.interactive:
    IPython.embed()

os.makedirs(args.output_folder, exist_ok=True)

with open(os.path.join(args.output_folder, '000_conference.txt'), 'w') as fp:

    def fprint(line, additional=None):
        fp.write(line + '\n')
        if additional: additional.write(line + '\n')
        print(line)

    for c in cs:
        fprint('----')
        slug = re.sub(r'\W+', '-', unidecode.unidecode(c['title']).lower())
        slug = slug[:22]
        try:
            # if numeric ID, convert it to a 3-digit number with leading zeros
            c['id'] = '{:03d}'.format(int(c['id']))
        except:
            pass
        with open(os.path.join(args.output_folder, c['id'] + '_' + slug + '.txt'), 'w') as cfp:
            with open(os.path.join(args.output_folder, c['id'] + '_' + slug + '.json'), 'w') as cfp_json:
                cfp_json.write(json.dumps(c))
            for prop in ('ID', 'Title', 'Type', 'Track'):
                fprint('{0}: {1}'.format(prop, c[prop.lower()]), cfp)
            fprint(c['description'], cfp)
            for people_group in ('primaryauthors', 'speakers', 'coauthors'):
                names = (a['fullName'] for a in c[people_group])
                names = (' '.join(name.split(', ')[::-1]) for name in names)
                fprint('{0}: {1}'.format(people_group.capitalize(), ', '.join(names)), cfp)
            attachments = []
            if 'folders' in c and len(c['folders']) >= 1:
                assert len(c['folders']) == 1
                assert 'attachments' in c['folders'][0]
                for a in c['folders'][0]['attachments']:
                    assert 'download_url' in a
                    if 'filename' not in a:
                        logger.warning('Cannot download this file: ' + a['download_url'])
                        continue
                    local_filename = c['id'] + '_' + a['filename']
                    attachments.append(local_filename)
                    abs_local_filename = os.path.join(args.output_folder, local_filename)
                    if os.path.isfile(abs_local_filename) and os.path.getsize(abs_local_filename) == a['size']:
                        logger.warning('file already there.')
                        continue
                    try:
                        with open(abs_local_filename, 'wb') as handle:
                            response = requests.get(a['download_url'], stream=True)
                            if not response.ok:
                                logger.warning("Couldn't download the file {}".format(local_filename))
                                continue
                            for block in response.iter_content(1024):
                                handle.write(block)
                    except KeyboardInterrupt as e:
                        # We don't want unfinished downloads
                        logger.warning('Ctrl-C - removing unfinished download: %s', local_filename)
                        os.unlink(abs_local_filename)
                        raise e
            fprint("Attachments: {}".format(' '.join(attachments)), cfp)
        fp.flush()

