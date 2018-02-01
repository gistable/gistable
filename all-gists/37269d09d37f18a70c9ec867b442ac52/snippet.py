#!/usr/bin/env python3
import tweepy
import re
import argparse
import sys
import time
import traceback

# Fill with your Twitter API keys!
consumer_key = ''
consumer_secret = ''
access_token = ''
access_token_secret = ''


class ReplyStreamListener(tweepy.StreamListener):
    def __init__(self, api, target_file, source_file):
        super().__init__(api)
        self.target_file = target_file
        self.source_file = source_file
        self.statuses = []
        self.username = re.compile('@\w{,15}')
        self.hashtag = re.compile('#\w+')
        self.retweet = re.compile('RT.?:?')
        self.url = re.compile('http\S+')

    def clean_twitter(self, text):
        text = self.username.sub('', text)
        text = self.hashtag.sub('', text)
        text = self.retweet.sub('', text)
        text = self.url.sub('', text)
        text = text.replace('\n', ' ')
        text = text.replace('\r', ' ')
        text = text.replace('\t', ' ')
        text = text.strip()
        return text

    def on_status(self, status):
        if status.in_reply_to_status_id_str is not None:
            self.statuses.append(status)

            # Accumulate 100 statuses and lookup batch of in_reply_to
            if len(self.statuses) == 100:
                in_reply_to_ids = [status.in_reply_to_status_id_str for status in self.statuses]

                # Note: response is smaller than request if some tweets were private (map_ arg does not work)
                source_statuses = self.api.statuses_lookup(in_reply_to_ids, trim_user=True)

                # Construct dictionary of source id to target text
                target_dictionary = {status.in_reply_to_status_id_str: status.text for status in self.statuses}

                for source_status in source_statuses:
                    # Lookup target text from source id
                    target_text = target_dictionary[source_status.id_str]

                    # Preprocessing for text format
                    source_text = self.clean_twitter(source_status.text)
                    target_text = self.clean_twitter(target_text)

                    # Save to text file
                    print(source_text, file=self.source_file)
                    print(target_text, file=self.target_file)

                self.statuses = []
                self.source_file.flush()
                self.target_file.flush()
                print('Collected', len(source_statuses), 'pairs')

    def on_error(self, status_code):
        print('Stream error with status code:', status_code, file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source_file', type=argparse.FileType('a'))
    parser.add_argument('target_file', type=argparse.FileType('a'))
    parser.add_argument('--languages', nargs='+', default=['ja'])
    args = parser.parse_args()

    while True:
        try:
            auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(access_token, access_token_secret)
            api = tweepy.API(auth)
            reply_stream_listener = ReplyStreamListener(api, args.target_file, args.source_file)
            reply_stream = tweepy.Stream(auth=api.auth, listener=reply_stream_listener)
            reply_stream.sample(languages=args.languages)
        except:
            traceback.print_exc(limit=10, file=sys.stderr, chain=False)
            time.sleep(60)
            continue

if __name__ == '__main__':
    main()
