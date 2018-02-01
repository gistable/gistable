#!/usr/bin/env python3

# Dependency: pip3 install twitter
import twitter

# Go to http://apps.twitter.com/, create an app, and fill in these values:
consumer_key = 'www'
consumer_secret = 'xxx'
access_token = 'yyy'
access_token_secret = 'zzz'


def twitter_login():
    """Connect to Twitter, returning a Twitter instance."""
    auth = twitter.OAuth(access_token, access_token_secret, consumer_key, consumer_secret)
    return twitter.Twitter(auth=auth, retry=True)


def unblock_all(t):
    """Unblock all blocked accounts, using the given Twitter instance."""
    blocked_count = 0

    while True:
        blocked_user_ids = t.blocks.ids()["ids"]
        if not blocked_user_ids:
            print("No more IDs to unblock")
            break

        for user_id in blocked_user_ids:
            blocked_count = blocked_count + 1
            print(f"{blocked_count}: {user_id}")
            try:
                t.blocks.destroy(user_id=user_id, include_entities=False, skip_status=True)
            except:
                print("error")


if __name__ == "__main__":
    t = twitter_login()
    unblock_all(t)
