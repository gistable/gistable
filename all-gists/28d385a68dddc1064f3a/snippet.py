import time
from slackclient import SlackClient

Token = 'token' #You must input your token key.
Chan = "C0XXXXXX" #You must input your slack channel code.
Text = "Test"  #Input your text.

sc = SlackClient(Token)
if sc.rtm_connect():
    while True:
        print("send")
        sc.rtm_send_message(Chan, Text)
        time.sleep(0.01)
else:
    print ("Connection Failed, invalid token?")
