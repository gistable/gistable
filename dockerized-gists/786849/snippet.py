#!/usr/bin/env python
"""
A simple script that extracts transcripts from <http://www.ted.com>

HOWTO:

	python ted_tracscript_extractor.py john_hodgman_s_brief_digression.html
	
	or
	
	python ted_tracscript_extractor.py http://www.ted.com/index.php/talks/john_hodgman_s_brief_digression.html

Copyright (c) 2010, Myles Braithwaite <me@mylesbraithwaite.com>
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:

* Redistributions of source code must retain the above copyright
  notice, this list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright
  notice, this list of conditions and the following disclaimer in
  the documentation and/or other materials provided with the
  distribution.

* Neither the name of the Monkey in your Soul nor the names of its
  contributors may be used to endorse or promote products derived
  from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS
OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY
WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""

import sys
import urllib2
from BeautifulSoup import BeautifulSoup

__version__ = '0.1'
__project_name__ = 'TedTranscriptExtractor'
__project_link__ = 'http://gist.github.com/786849'

TED_TALK_URL = 'http://www.ted.com/index.php/talks/'

def get_html(url):
	request = urllib2.Request(url)
	request.add_header('User-Agent', '%s/%s +%s' % (
		__project_name__, __version__, __project_link__
	))
	opener = urllib2.build_opener()
	return opener.open(request).read()

def main(talk_url):
	if not talk_url.startswith('http://'):
		talk_url = TED_TALK_URL + talk_url
	
	html = get_html(talk_url)
	
	soup = BeautifulSoup(html)
	
	transcript = soup.find('div', attrs={'id': 'transcriptText'})
	
	for p in transcript.findAll('p'):
		print ''.join(p.findAll(text=True))
		print

if __name__ == "__main__":
	talk_url = sys.argv[-1]
	main(talk_url)