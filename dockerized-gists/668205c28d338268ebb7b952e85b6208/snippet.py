import logging
import os
import time
import traceback


# pip install slackclient
from slackclient import SlackClient


SLACK_BOT_USER = 'YOUR_SLACK_BOT_USER_ID'
SLACK_BOT_MENTION = '<@%s>' % SLACK_BOT_USER
SLACK_BOT_NAME = 'nestor'
SLACK_CHANNEL = 'ask-nestor'

SLACK_TOKEN = os.environ.get('SLACK_TOKEN')

slack_client = SlackClient(SLACK_TOKEN)


class HelpException(Exception):
    pass


def send_message(text):
    slack_client.rtm_send_message(channel=SLACK_CHANNEL, message=text)


def has_conversation_started_with(user):
    pass


def process_conversation(cmd, event):
    pass


def process_help(*args):
    pass


def process_deploy(cmd, event):
    pass


def process_rollback(cmd, event):
    pass


def process_restart(cmd, event):
    pass


def process_event(event):
    # filter out slack events that are not for us
    text = event.get('text')
    if text is None or not text.startswith((SLACK_BOT_NAME, SLACK_BOT_MENTION)):
        return

    # make sure our bot is only called for a specified channel
    channel = event.get('channel')
    if channel is None:
        return
    if channel != sc.server.channels.find(SLACK_CHANNEL).id:
        send_message('<@{user}> I only run tasks asked from `{channel}` channel'.format(user=event['user'],
                                                                                        channel=SLACK_CHANNEL))
        return

    # remove bot name and extract command
    if text.startswith(SLACK_BOT_MENTION):
        cmd = text.split('%s' % SLACK_BOT_MENTION)[1]
        if cmd.startswith(':'):
            cmd = cmd[2:]
        cmd = cmd.strip()
    else:
        cmd = text.split('%s ' % SLACK_BOT_NAME)[1]

    # process command
    try:
        if has_conversation_started_with(event['user']):
            process_conversation(cmd, event)
        elif cmd.startswith('help'):
            process_help(cmd, event)
        elif cmd.startswith('deploy '):
            process_deploy(cmd, event)
        elif cmd.startswith('rollback '):
            process_rollback(cmd, event)
        elif cmd.startswith('restart '):
            process_restart(cmd, event)
        else:
            send_message("*I don't know how to do that*: `%s`" % cmd)
            process_help()
    except HelpException:
        return process_help()


def process_events(events):
    for event in events:
        try:
            process_event(event)
        except Exception as e:
            logging.exception(e)
            msg = '%s: %s\n%s' % (e.__class__.__name__, e, traceback.format_exc())
            send_message(msg)


def main():
    if slack_client.rtm_connect():
        send_message('_starting..._')

        # --
        # Here is a good place to init git repositories if needed, in order to provide git-based features:
        # - list of commits to deploy
        # - history of deployments
        # - status of deployed services vs what's available in git

        send_message("*All right, I'm ready, ask me anything!*")

        while True:
            events = slack_client.rtm_read()
            if events:
                logging.info(events)
            process_events(events)
            time.sleep(0.1)
    else:
        logging.error('Connection Failed, invalid token?')


if __name__ == '__main__':
    main()
