#!/usr/bin/env python

from __future__ import print_function
import requests
import sys
import json
import os


def hipchat_file(token, room, filepath, message='', host='api.hipchat.com'):
    """ Send file to a HipChat room via API version 2

    Parameters
    ----------
    token : str
        HipChat API version 2 compatible token - must be token for active user
    room: str
        Name or API ID of the room to notify
    filepath: str
        Full path of file to be sent
    message: str, optional
        Message to send to room
    host: str, optional
        Host to connect to, defaults to api.hipchat.com
    """

    if not os.path.isfile(filepath):
        raise ValueError("File '{0}' does not exist".format(filepath))
    if len(message) > 1000:
        raise ValueError('Message too long')

    url = "https://{0}/v2/room/{1}/share/file".format(host, room)
    headers = {'Content-type': 'multipart/related; boundary=boundary123456'}
    headers['Authorization'] = "Bearer " + token
    msg = json.dumps({'message': message})

    payload = """\
--boundary123456
Content-Type: application/json; charset=UTF-8
Content-Disposition: attachment; name="metadata"

{0}
--boundary123456
Content-Disposition: attachment; name="file"; filename="{1}"

{2}
--boundary123456--\
""".format(msg, os.path.basename(filepath), open(filepath, 'rb').read())

    r = requests.post(url, headers=headers, data=payload)
    r.raise_for_status()


my_token = 'MY_PERSONAL_HIPCHAT_TOKEN'
my_room = 'some_room_name_or_id'
my_file = '/path/to/some.file'
my_message = 'Check out this cool file'  # optional

try:
    hipchat_file(my_token, my_room, my_file, my_message)
except Exception as e:
        msg = "[ERROR] HipChat file failed: '{0}'".format(e)
        print(msg, file=sys.stderr)
        sys.exit(1)
