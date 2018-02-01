"""
Script to download all the books in a humble bundle.
May work for other resources, but don't have anything to test against.

To use, run from the directory you want to download the books in.
Pass the "game" key as the first argument (look in the URL of your normal download page).
To restrict to certain formats, pass them as extra positional arguments on the command line.

Example:
    python humble_bundle_download abcdef12345 mobi pdf

If no formats are passed, then all will be downloaded.

After this you'll have a new directory will all the books downloaded in the selected formats.

As written this script requires Python >= 3.6 due to use of f-strings.
Should be trivial to convert to other versions.

Thanks to https://www.schiff.io/projects/humble-bundle-api for discovering API endpoints.
Although that page mentions the API call we use requiring login, it worked without it
for me in the one case I've used it for. YMMV.
"""

import json
import os
import sys
import requests
from concurrent.futures import ThreadPoolExecutor, wait


def queue_downloads(game_key, *formats):
    formats = {f.lower() for f in formats}
    api_url = f'https://hr-humblebundle.appspot.com/api/v1/order/{game_key}'
    response = requests.get(api_url)
    response.raise_for_status()
    data = json.loads(response.text)
    bundle_name = data['product']['machine_name']
    dirname = os.path.join('.', bundle_name)
    try:
        os.mkdir(dirname)
    except FileExistsError:
        pass
    futures = []
    with ThreadPoolExecutor() as executor:
        for product in data['subproducts']:
            base = product['human_name']
            formats_to_urls = {
                dl_struct['name'].lower(): dl_struct['url']['web']
                for download in product['downloads']
                for dl_struct in download['download_struct']
            }
            if not formats_to_urls:
                print(f'Warning! Not downloads found for {base}...?')
                continue
            dl_data = {
                url: os.path.join(dirname, f'{base}.{fmt}')
                for fmt, url in formats_to_urls.items() if (not formats or fmt in formats)
            }
            if not dl_data:
                print(f'Warning! Not downloading {base} due to no acceptable formats.')
                continue
            futures.extend([executor.submit(do_download, *args) for args in dl_data.items()])
        wait(futures)


def do_download(url, out_path):
    r = requests.get(url)
    r.raise_for_status()
    with open(out_path, 'wb') as fd:
        fd.write(r.content)


if __name__ == '__main__':
    queue_downloads(*sys.argv[1:])
