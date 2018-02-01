# -*- coding: utf-8 -*-
from markdown import Extension
from markdown.util import etree
from markdown.inlinepatterns import Pattern

SOURCES = {
  "youtube": {
    "re": r'youtube\.com/watch\?\S*v=(?P<youtube>[A-Za-z0-9_&=-]+)',
    "embed": "//www.youtube.com/embed/%s"
  },
  "vimeo": {
    "re": r'vimeo\.com/(?P<vimeo>\d+)',
    "embed": "//player.vimeo.com/video/%s"
  }
}

VIDEO_LINK_RE = r'\!\[(?P<alt>[^\]]*)\]\((https?://(www\.|)({0}|{1})\S*)' \
                 r'(?<!png)(?<!jpg)(?<!jpeg)(?<!gif)\)'\
                  .format(SOURCES["youtube"]["re"], SOURCES["vimeo"]["re"])

class VideoExtension(Extension):
  """
  Embed Vimeo and Youtube videos in python markdown by using ![alt text](vimeo or youtube url)
  """
  def extendMarkdown(self, md, md_globals):
    link_pattern = VideoLink(VIDEO_LINK_RE, md)
    link_pattern.ext = self
    md.inlinePatterns.add('video_embed', link_pattern, '<image_link')

class VideoLink(Pattern):
  def handleMatch(self, match):
    alt = match.group("alt").strip()
    for video_type in SOURCES.keys():
      video_id = match.group(video_type)
      if video_id:
        html = self.make_url(video_id.strip(), video_type, alt)
        return self.markdown.htmlStash.store(html)
    return None

  def make_url(self, video_id, video_type, alt):
    url = SOURCES[video_type]["embed"] % video_id
    return self.video_iframe(url, alt, video_type=video_type)

  def video_iframe(self, url, alt, width=None, height=None, video_type=None):
    return u"<iframe class='{2}' src='{0}' alt='{1}' allowfullscreen></iframe>"\
      .format(url, alt, video_type)

def makeExtension(configs=None):
    return VideoExtension(configs=configs)