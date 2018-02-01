# Copyright (c) 2014 Andrey Vlasovskikh
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


"""tweetread - read and post tweets from the command line using asyncio.


    +---------+  stdin  +---------+  HTTP* +---------+
    | Console +---------> Twitter +--------> Twitter |
    |         <---------+ Client  |        | Server  |
    +---------+  stdout +----+----+        |         |
                             |popen        +---------+
                             |
                       +-----v--------+
                       | Notification |
                       +--------------+


Diagrams have been created using [asciiflow][1].


  [1]: http://asciiflow.com
"""

import sys
import json
import netrc
import asyncio
import textwrap
import logging
import traceback
from datetime import datetime
from contextlib import suppress

import aiohttp
import oauthlib.oauth1 as oauth


class TwitterClient:
    """Async Twitter client that maintains a persistent HTTP connection."""

    _TIMELINE_URL = 'https://api.twitter.com/1.1/statuses/home_timeline.json'

    # See also https://stream.twitter.com/1.1/statuses/sample.json for a sample
    # stream of various tweets
    _STREAM_URL = 'https://userstream.twitter.com/1.1/user.json'

    _STREAM_RETRY_TIMEOUT = 5.0

    def __init__(self, *, client_key, client_secret,
                 resource_owner_key, resource_owner_secret):
        self._oauth_client = (
            oauth.Client(client_key=client_key,
                         client_secret=client_secret,
                         resource_owner_key=resource_owner_key,
                         resource_owner_secret=resource_owner_secret))
        self._connector = aiohttp.TCPConnector()
        self._queue = asyncio.Queue()
        self._log = logging.getLogger(TwitterClient.__name__)
        self._subscribe_queue = asyncio.Queue()
        self._home_timeline = {}
        self._timeline_cached = False

    @asyncio.coroutine
    def run(self):
        """Launch the Twitter client."""
        asyncio.async(self._stream_subscription(self._subscribe_queue))
        asyncio.async(self._stream_events(self._subscribe_queue))

        yield from self.subscribe(self._queue)

        while True:
            msg = yield from self._queue.get()
            if isinstance(msg, self._HomeTimelineRequest):
                yield from self._get_home_timeline(msg.future)
            elif _is_tweet(msg):
                self._home_timeline[msg.get('id', 0)] = msg
            else:
                self._log.info('got unknown message: {}'.format(msg))

    @asyncio.coroutine
    def get_home_timeline(self):
        """Return the home timeline of the user.

        The home timeline is a collection of the most recent Tweets and
        re-tweets by the user and the users they follow.
        """
        response = asyncio.Future()
        yield from self._queue.put(self._HomeTimelineRequest(response))
        return (yield from response)

    @asyncio.coroutine
    def get_mentions_timeline(self):
        """Return the mentions timeline of the user.

        This timeline contains the most recent mentions (tweets containing a
        users' @screen_name) for the user.
        """
        raise NotImplementedError

    @asyncio.coroutine
    def post(self, tweet):
        """Post a new tweet by the user."""
        raise NotImplementedError

    @asyncio.coroutine
    def subscribe(self, queue):
        """Subscribe to the user stream of notifications.

        Notifications include new tweets, mentions, etc.
        """
        yield from self._subscribe_queue.put(self._Subscribe(queue))

    class _Request:
        def __init__(self, future: asyncio.Future):
            self.future = future

    class _HomeTimelineRequest(_Request):
        pass

    class _Subscribe:
        def __init__(self, publish_queue: asyncio.Queue):
            self.publish_queue = publish_queue

    @asyncio.coroutine
    def _stream_events(self, queue):
        first = False
        while True:
            if first:
                first = False
            else:
                yield from asyncio.sleep(self._STREAM_RETRY_TIMEOUT)

            try:
                response = yield from self._authorized_request('GET',
                                                               self._STREAM_URL)
                assert isinstance(response, aiohttp.client.HttpResponse)
                if response.status != 200:
                    raise Exception(response)
                try:
                    # Naive JSON stream reading
                    while True:
                        chunk = yield from response.content.read()
                        if chunk.strip() == b'':
                            continue
                        with suppress(UnicodeDecodeError, ValueError):
                            decoded = chunk.decode('utf-8')
                            msg = json.loads(decoded)
                            yield from queue.put(msg)
                except aiohttp.EofStream:
                    pass
            except Exception as e:
                self._log.error(e)

    @asyncio.coroutine
    def _get_home_timeline(self, future):
        if not self._timeline_cached:
            try:
                response = (
                    yield from self._authorized_request('GET',
                                                        self._TIMELINE_URL))
                assert isinstance(response, aiohttp.client.HttpResponse)
                if response.status != 200:
                    raise Exception(response)
                data = yield from response.read()
                timeline = json.loads(data.decode('utf-8'))
            except Exception as e:
                future.set_exception(e)
                return
            else:
                self._timeline_cached = True
                tweets = {tweet.get('id', 0): tweet for tweet in timeline}
                self._home_timeline.update(tweets)
        future.set_result(list(sorted(self._home_timeline.values(),
                                      key=self._get_tweet_created_at,
                                      reverse=True)))

    @asyncio.coroutine
    def _authorized_request(self, method, url):
        signed = self._oauth_client.sign(url, method)
        _, signed_headers, _ = signed
        return (yield from aiohttp.request(method, url,
                                           headers=signed_headers,
                                           connector=self._connector))

    @classmethod
    @asyncio.coroutine
    def _stream_subscription(cls, queue):
        subscriptions = []
        while True:
            msg = yield from queue.get()
            if isinstance(msg, cls._Subscribe):
                subscriptions.append(msg.publish_queue)
            else:
                for subscription in subscriptions:
                    yield from subscription.put(msg)

    @staticmethod
    def _get_tweet_created_at(tweet):
        created_at = tweet.get('created_at', '')
        try:
            return datetime.strptime(created_at, '%a %b %d %H:%M:%S +0000 %Y')
        except ValueError:
            return datetime(1900, 1, 1)


class Console:
    """Command line based user input and output."""

    _SCREEN_WIDTH = 80

    def __init__(self):
        self._output = asyncio.Queue()

        credentials = netrc.netrc().authenticators('api.twitter.com')
        if not credentials:
            raise Exception('OAuth credentials not found in ~/.netrc')
        login, _, password = credentials
        resource_owner_key, client_key = login.split('&', 1)
        resource_owner_secret, client_secret = password.split('&', 1)

        self._twitter_client = (
            TwitterClient(client_key=client_key,
                          client_secret=client_secret,
                          resource_owner_key=resource_owner_key,
                          resource_owner_secret=resource_owner_secret))

    @asyncio.coroutine
    def run(self):
        """User commands input loop.

        Parse user commands and send appropriate requests to Twitter.
        """
        asyncio.async(self._handle_output_events())
        asyncio.async(self._twitter_client.run())

        yield from self._twitter_client.subscribe(self._output)
        self._async_request_home_timeline()

        reader = yield from self._make_pipe_reader(sys.stdin)
        assert isinstance(reader, asyncio.StreamReader)
        while not reader.at_eof():
            line = (yield from reader.readline()).decode('utf-8').strip()
            yield from self._output.put('')
            if line == 'quit':
                return
            elif line == 'help':
                text = 'commands: home, help, quit'
                yield from self._output.put(text)
            elif line == 'home':
                self._async_request_home_timeline()
            elif line == '':
                continue
            else:
                bad_cmd = "bad command, type 'help' for more info"
                yield from self._output.put(bad_cmd)

    def _async_request_home_timeline(self):
        self._async_to_output(self._twitter_client.get_home_timeline(),
                              wrapper=self._HomeTimelineResponse)

    def _async_to_output(self, coroutine, *, wrapper):

        @asyncio.coroutine
        def helper():
            try:
                result = wrapper((yield from coroutine))
            except Exception as e:
                result = e
            yield from self._output.put(result)

        asyncio.async(helper())

    @staticmethod
    @asyncio.coroutine
    def _make_pipe_reader(pipe):
        """Return an async StreamReader for a pipe."""
        loop = asyncio.get_event_loop()
        reader = asyncio.StreamReader()
        factory = lambda: asyncio.StreamReaderProtocol(reader)
        yield from loop.connect_read_pipe(factory, pipe)
        return reader

    @asyncio.coroutine
    def _handle_output_events(self):
        """Process output events and display them accordingly."""
        prompt = '> '
        clear = '\r' + ' ' * self._SCREEN_WIDTH + '\r'
        while True:
            print(prompt, end='', flush=True)
            try:
                msg = yield from self._output.get()
                print(clear, end='', flush=True)
                if isinstance(msg, self._HomeTimelineResponse):
                    for tweet in reversed(msg.data):
                        print(self._pretty_tweet(tweet))
                elif _is_tweet(msg):
                    print(self._pretty_tweet(msg))
                elif isinstance(msg, str):
                    if msg != '':
                        print(msg)
                elif isinstance(msg, Exception):
                    raise msg
                else:
                    logging.info('got unknown message: {}'.format(msg))
            except Exception:
                traceback.print_exc()

    @classmethod
    def _pretty_tweet(cls, tweet):
        username = tweet.get('user', {}).get('screen_name', '(unknown)')
        text = tweet.get('text', '(empty)')
        return '<{user}> {msg}'.format(user=username,
                                       msg=cls._wrap_string(text).lstrip())

    @staticmethod
    def _wrap_string(string, *, indent=6, width=80):
        return '\n'.join((' ' * indent) + line
                         for line in textwrap.wrap(string, width))

    class _Wrapper:
        def __init__(self, data):
            self.data = data

    class _HomeTimelineResponse(_Wrapper):
        pass


def _is_tweet(x):
    return isinstance(x, dict) and 'retweeted' in x


def main():
    try:
        loop = asyncio.get_event_loop()
        task = asyncio.async(Console().run())
        loop.run_until_complete(task)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
