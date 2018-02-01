import tweets
import datetime
import sys

def retrieve_conversations(tweets):
    """ Retrieves tweets with conversations.

    To determine if a tweet is a part of conversation,
    it uses user-mentions field in the tweet-entities.
    So, the inherent assumption is that the tweets
    are not returned from the search API.

    For more details, see https://dev.twitter.com/docs/tweet-entities
    """

    li = []
    for tweet in tweets:
        if tweet.entities['user_mentions']:
            li.append((tweet.created_at,
                len(tweet.entities['user_mentions'])))

    return li

def aggregate_conversations(li, delta):
    """Aggregates the conversation count.
    
    Keyword arguments:
        li --- The list of tuples containing tweet creation date
            and number of user mentions.
        delta --- The timedelta object by which the conversations
            should be aggregated.

    """

    count = []
    date = []

    index = -1

    for (d, c) in sorted(li):
        if index == -1:
            index += 1
            count.append(c)
            date.append(d)
        else:
            if d - date[index] <= delta:
                count[index] += c
            else:
                date.append(d)
                count.append(c)
                index += 1
    return (count, date)


def draw_conversation(c, d, title):
    """Draws the conversation graphs."""

    import matplotlib.pyplot as plt
    import numpy as np

    mentions = np.array(c, dtype='int32')

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.scatter(d, mentions, c=mentions, s=mentions**1.5, alpha=0.75 )

    plt.title(title)

    plt.show()

def main(argv):

    #Aggregate by a week
    agg_range=7

    if argv:
        defaults, user_info = tweets.parse_config(argv[0])
        
        statuses = tweets.get_user_status(user_info[0], user_info[1])

        li = retrieve_conversations(statuses)
        (c, d) = aggregate_conversations(li, datetime.timedelta(days=agg_range))
        title = " Conversations of " + user_info[0]
        draw_conversation(c, d, title)


if __name__ == "__main__":
    main(sys.argv[1:])