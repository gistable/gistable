import mimetypes
import pprint
import requests  # pip install requests
import simplejson as json

from os.path import basename, expanduser

base_url = 'https://alpha-api.app.net/stream/0'
token = 'USER ACCESS TOKEN'
image_path = 'PATH TO FILE'
post_text = 'my post text'

r = requests.session()
r.headers.update({'Authorization': 'Bearer %s' % (token)})

# post file
with open(expanduser(image_path)) as fp:
    filename = basename(fp.name)
    mimetype, _ = mimetypes.guess_type(filename)
    mimetype = mimetype or 'application/octet-stream'
    image_resp = r.post(base_url + '/files', files={'content': (filename, fp, mimetype)}, data={'type': 'com.mthurman.sample_code'})

image_data = image_resp.json()['data']

# make a post with file attached
post = {
    'text': post_text,
    'annotations': [
        {
            "type": "net.app.core.oembed",
            "value": {
                "+net.app.core.file": {
                    "file_id": image_data['id'],
                    "file_token": image_data['file_token'],
                    "format": "oembed"
                }
            }
        },
        {
            "type": "net.app.core.attachments",
            "value": {
                "+net.app.core.file_list": [
                    {
                        "file_id": image_data['id'],
                        "file_token": image_data['file_token'],
                        "format": "metadata"
                    },
                ]
            }
        }
    ]
}

post_resp = r.post(base_url + '/posts?include_post_annotations=1', json.dumps(post), headers={'Content-Type': "application/json"})
pprint.pprint(post_resp.json())
