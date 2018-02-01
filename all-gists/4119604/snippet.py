"Build a road-trip curated mp3 directory of a podcast."

# Developed against feedparser v5.1.2 and BeautifulSoup v3.2.1.
# pip install feedparser BeautifulSoup

import datetime
import re
import time
import urllib

import BeautifulSoup
import feedparser


def strip_tags(text):
    soup = BeautifulSoup.BeautifulSoup(text)
    for tag in soup.findAll(True):
        text_content = ''
        for content in tag.contents:
            if not isinstance(content, BeautifulSoup.NavigableString):
                content = strip_tags(unicode(content))
            text_content += unicode(content)
        tag.replaceWith(text_content)
    return unicode(soup)


def replace_non_ascii(text, replacement):
    "This module works with simple ASCII. This function supports that."
    def cleaned(char):
        if ord(char) < 128:
            return char
        return replacement
    return ''.join(cleaned(char) for char in text)


class Episode(object):
    "Takes a podcast feed item and provides for organized download."

    def __init__(self, entry):
        self.handle_entry(entry)

    def handle_entry(self, entry):
        self.title = entry.title
        self.description = strip_tags(entry.description)

        # Note that published is time of podcast publish, not air date.
        self.published = entry.published
        timestamp = time.mktime(entry.published_parsed)
        self.datetime = datetime.datetime.fromtimestamp(timestamp)

        # Get the first mp3 linked in the enclosures.
        for link in entry.links:
            if link.type == 'audio/mpeg':
                self.url = link.href
                break
        else:
            raise RuntimeError('No mp3 found:\n' + repr(entry))

    def generate_filename(self, words=6):
        tokens = self.title.split(' ')
        stub = ' '.join(tokens[:words])
        stripped = re.sub('[^a-zA-Z0-9 -]', '', stub)
        return stripped.replace(' ', '_').lower()

    def summarize(self):
        "Summarize in ASCII to provide simplest text summary."
        summary = u'{0}\n\n{1}\n'.format(self.title, self.description)
        return replace_non_ascii(summary, ' ')

    def save(self, prefix):
        filename = '{0}_{1}'.format(prefix, self.generate_filename())
        # open('{0}.mp3'.format(filename), 'w').close()
        urllib.urlretrieve(self.url, '{0}.mp3'.format(filename))
        with open('{0}.txt'.format(filename), 'wb') as fd:
            fd.write(self.summarize())


def download(fd):
    feed = feedparser.parse(fd)
    for index, entry in enumerate(feed.entries, 1):
        episode = Episode(entry)
        prefix = str(index).zfill(2)
        print episode.generate_filename()
        episode.save(prefix)

# The Podcast URLs from the Best of Fresh Air.
#
# http://www.npr.org/series/132148276/the-best-of-fresh-air-2010
# 2010: http://www.npr.org/templates/rss/podlayer.php?id=132148276
#
# http://www.npr.org/series/144011437/the-best-of-fresh-air-2011
# 2011: http://www.npr.org/templates/rss/podlayer.php?id=144011437

# Create directory 2010, then uncomment, running inside that 2010 directory:
# download(urllib.urlopen('http://www.npr.org/templates/rss/podlayer.php?id=132148276'))

# Create directory 2011, then uncomment, running inside that 2011 directory:
# download(urllib.urlopen('http://www.npr.org/templates/rss/podlayer.php?id=144011437'))

# Try it with other podcast URLs, too.
# download(urllib.urlopen('http://www.npr.org/rss/podcast.php?id=13'))

if __name__ == '__main__':
    # Take the podcast URL from the command line.
    import sys
    download(urllib.urlopen(sys.argv[1]))