#! /usr/bin/env python3
'''lcp_export.py
Extracts URL schemes from a Launch Center Pro backup file to a
json file, in order to facilitate batch editing on a computer. Also
creates an updated backup file after modification of the json.
python3 lcp_export.py --help
Details: http://n8h.me/1meUxTi
'''

import re
import subprocess
import time
import json
import argparse
import html
import html.parser

import logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename='lcp_export.log',
    filemode='a'
    )

logger_name = str(__file__) + " :: " + str(__name__)
logger = logging.getLogger(logger_name)

ts = str(int(time.time()))

out_xml = '{}_xml.lcpbackup'.format(ts)
out_binary = '{}_binary.lcpbackup'.format(ts)
out_json = '{}_lcp_urls.json'.format(ts)

def read_lcp_backup(lcp_file):
    args = ['plutil', '-convert', 'xml1', lcp_file, '-o', out_xml]
    subprocess.call(args)
    with open(out_xml) as r:
        pl = r.read()
    return pl

def find_urls(pl):

    urls_dict = {}

    marker = re.compile(
        r'<string>x-coredata://.*?/LaunchAction/(p\d+)</string>' \
        '\s+?<string>(.*?)</string>' \
        '\s+?<string>(.*?)</string>'
        )

    for each_url in re.finditer(marker, pl):
        try:
            url_id = each_url.group(1)
            url_title_raw =  each_url.group(2)
            url_content_raw =  each_url.group(3)
        except AttributeError as e:
            logger.error("Problem matching {}".format(each_url.group(0)))

        url_title = html.parser.HTMLParser().unescape(url_title_raw)
        url_content = html.parser.HTMLParser().unescape(url_content_raw)

        urls_dict.update({url_id: {'title': url_title, 'url': url_content}})

    return urls_dict

def update_pl(pl, my_json):

    for url_scheme in my_json:
        marker = re.compile(
            r'(<string>x-coredata://.*?/LaunchAction/{}</string>' \
            '\s+?<string>).*?(</string>' \
            '\s+?<string>).*?(</string>)'.format(url_scheme)
            )

        # todo: Do I need to html encode / decode quotes?
        url_title = my_json[url_scheme]['title']
        url_content = my_json[url_scheme]['url']

        url_title_encoded = html.escape(url_title)
        url_content_encoded = html.escape(url_content)

        pl = re.sub(marker, r'\g<1>{}\g<2>{}\g<3>'.format(url_title_encoded,
                                                    url_content_encoded), pl)
    return pl

def write_lcp_backup(new_pl):

    with open(out_binary, 'w') as w:
        w.write(new_pl)

    args = ['plutil', '-convert', 'binary1', out_binary]
    subprocess.call(args)

    print("Output:\n{}".format(out_binary))
    return

def main():

    description = 'Make Launch Center Pro backup files easier to work with.'
    parser = argparse.ArgumentParser(description=description)
    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument('-read', action='store', help = ('Read in '
    'a Launch Center Pro .lcpbackup file and output a json file with '
    'the URL actions.'))

    group.add_argument('-write', action='store', help = ('Read in a '
    'previously created json file and write it to a Launch Center Pro '
    'backup file.'))

    parser.add_argument('-lcpfile', '-l', action='store', help=('The '
    '*XML* LCP backup file to use as a template (defaults to xml file with '
    'same timestamp as json file. Either use the default, or convert manually '
    'from binary to xml with plutil.'))

    args = parser.parse_args()

    if args.read:
        if not args.read.endswith('.lcpbackup'):
            print("You need to specify an .lcpbackup file to read.")
            exit(0)
        else:
            pl = read_lcp_backup(args.read)

            url_dict = find_urls(pl)

            with open(out_json, 'w') as json_opener:
                json.dump(url_dict, json_opener, indent=4)

            print("Output:\n{}\n{}".format(out_json, out_xml))

    if args.write:
        if not args.write.endswith('.json'):
            print("You need to specify a .json file to read from.")
            exit(0)
        else:

            old_ts = re.search(r'^\d+', args.write).group(0)
            template_file = '{}_xml.lcpbackup'.format(old_ts)

            if args.lcpfile:
               template_file = args.lcpfile

            with open(template_file) as xml, \
                        open(args.write) as json_file:

                pl = xml.read()
                my_json = json.load(json_file)

            new_pl = update_pl(pl, my_json)

            write_lcp_backup(new_pl)

if __name__ == '__main__':
    main()
