import json
import uuid

from pathlib import Path
from urllib.parse import urlparse
from datetime import datetime

import html2text
import requests
from bs4 import BeautifulSoup


source_url = 'http://tomaugspurger.github.io/modern-5-tidy.html'
IP_URL = 'http://www.instapaper.com/text?u={url}'
QVR_NOTEBOOK = '/Users/kristof/Dropbox/Applications/Quiver/Quiver.qvlibrary/F54CCC03-A5EC-48E7-8DCD-A264ABCC4277.qvnotebook'


# Download the images and generate UUIDs
def localize_images(resource_path, img_tags):

    for img_tag in img_tags:
        url = img_tag['src']
        r = requests.get(url)
        
        # Define the extension and the new filename
        img_ext = Path(urlparse(url).path).suffix
        img_name = '{}{}'.format(uuid.uuid4().hex.upper(),
                                 img_ext)
        img_filename = Path(resource_path, img_name)
        
        with open(str(img_filename), 'wb') as f:
            f.write(r.content)
        
        # Convert the original URL to a Quiver URL
        img_tag['src'] = 'quiver-image-url/{}'.format(img_name)


# Write content.json
def write_content(note_path, note_title, note_text):
    qvr_content = {}
    qvr_content['title'] = note_title
    qvr_content['cells'] = []
    cell = {'type': 'markdown', 
            'data': note_text}
    qvr_content['cells'].append(cell)

    with open(str(Path(note_path, 'content.json')), 'w') as f:
        f.write(json.dumps(qvr_content))


# Write meta.json
def write_meta(note_path, note_title, note_uuid):
    timestamp = int(datetime.timestamp(datetime.now()))
    qvr_meta = {}
    qvr_meta['title'] = note_title
    qvr_meta['uuid'] = note_uuid
    qvr_meta['created_at'] = timestamp
    qvr_meta['updated_at'] = timestamp

    with open(str(Path(note_path, 'meta.json')), 'w') as f:
        f.write(json.dumps(qvr_meta))


# Download the IP version of the URL
r = requests.get(IP_URL.format(url=source_url))
r.raise_for_status()
bs = BeautifulSoup(r.content, 'lxml')

qvr_note_uuid = str(uuid.uuid4()).upper()

# Create the folders
paths = {}
paths['notebook'] = QVR_NOTEBOOK
paths['note'] = Path(paths['notebook'], '{}.qvnote'.format(qvr_note_uuid))
paths['resources'] = Path(paths['note'], 'resources')
paths['resources'].mkdir(parents=True, exist_ok=True)

# Replace the original links by the quiver links
localize_images(paths['resources'], bs.find_all('img'))

# Remove title
_ = bs.select('body  main > div.titlebar')[0].extract()

# Convert to Markdown
parser = html2text.HTML2Text()
parser.protect_links = True
parser.wrap_links = False
parser.body_width = 0
note_text = parser.handle(str(bs.find('main')))

write_content(paths['note'], 
              bs.head.title.string,
              note_text)

write_meta(paths['note'], 
              bs.head.title.string,
              qvr_note_uuid)
