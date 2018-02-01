import json
import markovify
import re
import time

from slackclient import SlackClient



BOT_TOKEN = "insert bot token here"
GROUP_TOKEN = "insert user token here"
MESSAGE_QUERY = "from:user_to_mimic"

MESSAGE_PAGE_SIZE = 100

DEBUG = True



def _load_db():
    """
    Reads 'database' from a JSON file on disk.
    Returns a dictionary keyed by unique message permalinks.
    """

    with open('message_db.json', 'r') as json_file:
        messages = json.loads(json_file.read())

    return messages

def _store_db(obj):
    """
    Takes a dictionary keyed by unique message permalinks and writes it to the JSON 'database' on
    disk.
    """

    with open('message_db.json', 'w') as json_file:
        json_file.write(json.dumps(obj))

    return True

def _query_messages(client, page=1):
    """
    Convenience method for querying messages from Slack API.
    """
    if DEBUG:
        print "requesting page {}".format(page)

    return client.api_call('search.messages', query=MESSAGE_QUERY, count=MESSAGE_PAGE_SIZE, page=page)

def _add_messages(message_db, new_messages):
    """
    Search through an API response and add all messages to the 'database' dictionary.
    Returns updated dictionary.
    """
    for match in new_messages['messages']['matches']:
        message_db[match['permalink']] = match['text']

    return message_db


# get all messages, build a giant text corpus
def build_text_model():
    """
    Read the latest 'database' off disk and build a new markov chain generator model.
    Returns TextModel.
    """
    if DEBUG:
        print "Building new model..."

    messages = _load_db()
    return markovify.Text(" ".join(messages.values()), state_size=2)


def format_message(original):
    """
    Do any formatting necessary to markon chains before relaying to Slack.
    """
    if original is None:
        return

    # Clear <> from urls
    cleaned_message = re.sub(r'<(htt.*)>', '\1', original)

    return cleaned_message


def update_corpus(sc, channel):
    """
    Queries for new messages and adds them to the 'database' object if new ones are found.
    Reports back to the channel where the update was requested on status.
    """

    sc.rtm_send_message(channel, "Leveling up...")

    # Messages will get queried via user token from the Slack group.
    group_sc = SlackClient(GROUP_TOKEN)

    # Load the current database
    messages_db = _load_db()
    starting_count = len(messages_db.keys())

    # Get first page of messages
    new_messages = _query_messages(group_sc)
    total_pages = new_messages['messages']['paging']['pages']

    # store new messages
    messages_db = _add_messages(messages_db, new_messages)

    # If any subsequent pages are present, get those too
    if total_pages > 1:
        for page in range(2, total_pages + 1):
            new_messages = _query_messages(group_sc, page=page)
            messages_db = _add_messages(messages_db, new_messages)

    # See if any new keys were added
    final_count = len(messages_db.keys())
    new_message_count = final_count - starting_count

    # If the count went up, save the new 'database' to disk, report the stats.
    if final_count > starting_count:
        # Write to disk since there is new data.
        _store_db(messages_db)
        sc.rtm_send_message(channel, "I have been imbued with the power of {} new messages!".format(
            new_message_count
        ))
    else:
        sc.rtm_send_message(channel, "No new messages found :(")

    if DEBUG:
        print("Start: {}".format(starting_count), "Final: {}".format(final_count),
              "New: {}".format(new_message_count))

    # Make sure we close any sockets to the other group.
    del group_sc

    return new_message_count