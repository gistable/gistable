import httplib2
import os
import sys

from apiclient.discovery import build
# from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run

from urlparse import urlparse, parse_qs
import re
from docopt import docopt
import fileinput


# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the Google Cloud Console at
# https://cloud.google.com/console.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets


CLIENT_SECRETS_FILE = "client_secrets.json"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

%s

with information from the Cloud Console
https://cloud.google.com/console

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                           CLIENT_SECRETS_FILE))

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account.
YOUTUBE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def video_id(url):
    """
    Examples:
    - http://youtu.be/SA2iWivDJiE
    - http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu
    - http://www.youtube.com/embed/SA2iWivDJiE
    - http://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US
    - www.youtube.com/embed/SA2iWivDJiE
    - http://youtu.be.com/SA2iWivDJiE
    - youtube.com/embed/SA2iWivDJiE
    - SA2iWivDJiE

    From http://stackoverflow.com/a/7936523
    Edited to support optional url scheme and only video_id
    """
    query = urlparse(url)

    if not query.scheme:
        url = "http://" + url
        query = urlparse(url)
    #http://stackoverflow.com/q/6344993

    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            p = parse_qs(query.query)
            return p['v'][0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
    #match for a video_id as a argument
    if re.match('[a-zA-Z0-9_-]{11}', url):
        return url
    return None


def get_authenticated_service():
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=YOUTUBE_SCOPE,
    message=MISSING_CLIENT_SECRETS_MESSAGE)

    storage = Storage("%s-oauth2.json" % sys.argv[0])
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        credentials = run(flow, storage)

    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
        http=credentials.authorize(httplib2.Http()))

def get_videos_from_playlist(youtube, items, playlistID):
    response = items.list(part="snippet", playlistId=playlistID)
    while response:
        playlistitems_list_response = response.execute()

        for playlist_item in playlistitems_list_response["items"]:
            # title = playlist_item["snippet"]["title"]
            video_id = playlist_item["snippet"]["resourceId"]["videoId"]
            yield video_id

        response = youtube.playlistItems().list_next(
        response, playlistitems_list_response)


def add_video_to_playlist(youtube,playlistID, videoID):
    items = youtube.playlistItems()
    playlist = get_videos_from_playlist(youtube, items, playlistID)
    if videoID not in playlist:
        add_video_request=items.insert(
        part="snippet",
        body={
            'snippet': {
              'playlistId': playlistID,
              'resourceId': {
                      'kind': 'youtube#video',
                  'videoId': videoID
                }
            #'position': 0
            }
        }
        ).execute()
        return add_video_request
    print "Already on Playlist"
    return None

def add_file_to_playlist(youtube, playlistID, finput):
    for line in finput:
        videoID = video_id(line.strip())
        try:
            add_video_to_playlist(youtube, playlistID, videoID)
        except Exception, e:
            print "Couldn't add video: {0}\n{1}\n".format(videoID, e)


if __name__ == '__main__':

    docs = \
    """Add to youtube playlist

        Usage:
            add2ytpl.py add <playlistID> <videoID>...
            add2ytpl.py addFile <playlistID> [<filename>...]
            add2ytpl.py (-h | --help)

        Options:
            -h --help     Show this screen.
    """

    args = docopt(docs)
    # print(args)

    youtube = get_authenticated_service()
    if args['add']:
        for video in args['<videoID>']:
            add_video_to_playlist(youtube, args['<playlistID>'], video_id(video))
    if args['addFile']:
        f = fileinput.input(args['<filename>'])
        add_file_to_playlist(youtube, args['<playlistID>'], f)
