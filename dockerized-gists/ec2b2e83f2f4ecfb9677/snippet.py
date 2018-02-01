# HTTPS youtube embeds for wagtail
# Put this file in your project and add the following to your settings:
# WAGTAILEMBEDS_EMBED_FINDER = 'myapp.embeds.custom_embed_finder'


import json
import re

from six.moves.urllib.request import Request, urlopen
from six.moves.urllib.error import URLError
from six.moves.urllib.parse import urlencode

from wagtail.wagtailembeds.embeds import oembed


def is_youtube(url):
    YOUTUBE_ENDPOINTS = [
        "^http(?:s)?://(?:[-\\w]+\\.)?youtube\\.com/watch.+$",
        "^http(?:s)?://(?:[-\\w]+\\.)?youtube\\.com/v/.+$",
        "^http(?:s)?://youtu\\.be/.+$",
        "^http(?:s)?://(?:[-\\w]+\\.)?youtube\\.com/user/.+$",
        "^http(?:s)?://(?:[-\\w]+\\.)?youtube\\.com/[^#?/]+#[^#?/]+/.+$",
        "^http(?:s)?://m\\.youtube\\.com/index.+$",
        "^http(?:s)?://(?:[-\\w]+\\.)?youtube\\.com/profile.+$",
        "^http(?:s)?://(?:[-\\w]+\\.)?youtube\\.com/view_play_list.+$",
        "^http(?:s)?://(?:[-\\w]+\\.)?youtube\\.com/playlist.+$"
    ]

    for pattern in YOUTUBE_ENDPOINTS:
        if re.match(pattern, url):
            return True

    return False


def youtube_https(url, max_width=None):
    # Work out params
    params = {'url': url, 'format': 'json', 'scheme': 'https'}
    if max_width:
        params['maxwidth'] = max_width

    # Perform request
    request = Request('https://www.youtube.com/oembed?' + urlencode(params))
    request.add_header('User-agent', 'Mozilla/5.0')
    try:
        r = urlopen(request)
    except URLError:
        return

    oembed = json.loads(r.read().decode('utf-8'))

    # Return embed as a dict
    return {
        'title': oembed['title'] if 'title' in oembed else '',
        'author_name': oembed['author_name'] if 'author_name' in oembed else '',
        'provider_name': oembed['provider_name'] if 'provider_name' in oembed else '',
        'type': oembed['type'],
        'thumbnail_url': oembed['thumbnail_url'],
        'width': oembed['width'],
        'height': oembed['height'],
        'html': oembed['html'],
    }


def custom_embed_finder(url, max_width):
    if is_youtube(url):
        youtube = youtube_https(url, max_width)
        if youtube:
            return youtube

    # Fall back to oembed if the requested URL is not for youtube
    return oembed(url, max_width)