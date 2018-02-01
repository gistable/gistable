'''
This is an example of how to use the Slack Real Time Messaging API using
Python and the python-slackclient.
The example below originates from the python-slackclient documentation.
See https://github.com/slackhq/python-slackclient#real-time-messaging


This is everything you can do with the client:

Connect to a Slack RTM websocket. This is a persistent connection from which you can read events.
SlackClient.rtm_connect()

Read all data from the RTM websocket. Multiple events may be returned,
always returns a list [], which is empty if there are no incoming messages.
SlackClient.rtm_read()

Sends the text in [message] to [channel], which can be a name or identifier i.e. "#general" or "C182391"
SlackClient.rtm_send_message([channel, message])
e.g. sc.rtm_send_message('#general', 'https://m.popkey.co/988a17/3RkD5.gif')

Call the Slack method [method]. Arguments can be passed as kwargs, for instance: sc.api_call('users.info', user='U0L85V3B4')
SlackClient.api_call([method])

Send a JSON message directly to the websocket.
See RTM documentation for allowed types https://api.slack.com/rtm
SlackClient.server.send_to_websocket([data])

The identifier can be either name or Slack channel ID.
SlackClient.server.channels.find([identifier])

Send message [text] to [int] channel in the channels list.
SlackClient.server.channels[int].send_message([text])

Send message [text] to channel [identifier], which can be either channel name or ID. Ex "#general" or "C182391"
SlackClient.server.channels.find([identifier]).send_message([text])

Server object owns the websocket and all nested channel information.
SlackClient.server

A searchable list of all known channels within the parent server. Call print (sc instance) to see the entire list.
SlackClient.server.channels

'''

import time
from slackclient import SlackClient

token = 'xoxp-28192348123947234198234'  # found at https://api.slack.com/web#authentication
sc = SlackClient(token)
if sc.rtm_connect():  # connect to a Slack RTM websocket
    while True:
        print sc.rtm_read()  # read all data from the RTM websocket
        time.sleep(1)
else:
    print 'Connection Failed, invalid token?'
