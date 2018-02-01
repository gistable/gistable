"""
pyhowl - Post to Howl (http://howlapp.com)

Copyright (c) 2011, Jeff Triplett
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

 * Redistributions of source code must retain the above copyright notice,
   this list of conditions and the following disclaimer.
 * Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.
 * Neither the name of  nor the names of its contributors may be used to
   endorse or promote products derived from this software without specific
   prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.

Inspiration / optparse modified from @zacharyvoase via:
    https://gist.github.com/141757

"""
import optparse
import requests


class HowlEvent(object):

    """ Class representing a single Howl event."""

    DEFAULT_USER_AGENT = 'PyHowl/0.1'

    def __init__(self, application, name, title, description):
        self.application = application
        self.name = name
        self.title = title
        self.description = description

    @property
    def url(self):
        url = 'https://howlapp.com/public/api/notification'
        return url

    def request(self, username, password, user_agent=DEFAULT_USER_AGENT):
        request = requests.post(self.url,
            auth=(username, password),
            headers={'User-agent': user_agent},
            data={
                'application': self.application,
                'name': self.name,
                'title': self.title,
                'description': self.description,
                'icon-md5': 'dc0f5209059a0e7f3ff298680f98bc1b',
                'icon-sha1': '22339dd6e17eb099ed023c72bd7b5deaf785f2bb',
            }
        )
        return request

OPTION_PARSER = optparse.OptionParser(version='0.1')
OPTION_PARSER.add_option('-u', '--username', help='Howl username')
OPTION_PARSER.add_option('-p', '--password', help='Howl password')
OPTION_PARSER.add_option('-a', '--application', default="PyHowl",
    help='Name of source application (default "PyHowl")')
OPTION_PARSER.add_option('-n', '--name', help='Name of event')
OPTION_PARSER.add_option('-t', '--title', help='Title of event')
OPTION_PARSER.add_option('-d', '--description', help='Description of event')
OPTION_PARSER.add_option('-g', '--user-agent',
    default=HowlEvent.DEFAULT_USER_AGENT,
    help='User-agent string (default "%s")' % HowlEvent.DEFAULT_USER_AGENT)


def main():
    options, args = OPTION_PARSER.parse_args()

    event = HowlEvent(options.application, options.name, options.title,
        options.description)
    request = event.request(options.username, options.password,
        user_agent=options.user_agent)

    if request.status_code == 401:
        print 'Notification posting failed (invalid username or password)'
        raise SystemExit(1)

    print 'Notification successfully posted.'


if __name__ == '__main__':
    main()
