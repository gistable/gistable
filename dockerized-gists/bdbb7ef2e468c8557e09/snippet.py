#!/usr/bin/env python
"""
    Python Module Depedencies:
    ==========================
    falcon
    requests
"""
import falcon
import json
import requests

from wsgiref import simple_server

SLACK_WEB_HOOK_HOST = "<HOSTNAME_OR_IP_ADDRESS>" #Hostname or IP Address of the Bitbucket POST Hook receiver
SLACK_WEB_HOOK_PORT = 8081 #You know the drill!!!

SLACK_INCOMING_WEB_HOOK = "<SLACK_INCOMING_WEB_HOOK_URL>" #self explanatory or not???
SLACK_INCOMING_USER = "SlackBit Bot" #Slack Bot display name
SLACK_INCOMING_CHANNEL = "#general" #Slack Channel

def send_slack_message(dictMsg):

    payload = {
        "text": "",
        "username": SLACK_INCOMING_USER,
        "channel": SLACK_INCOMING_CHANNEL
    }

    if dictMsg:

        userLink = "<%s/%s|%s>" % (dictMsg["canon_url"], dictMsg["user"], dictMsg["user"])
        commitCount = len(dictMsg["commits"])
        repoUrlRoot = "%s%s" % (dictMsg["canon_url"], dictMsg["repository"]["absolute_url"])
        repoURL = "<%s|%s>" % (repoUrlRoot, dictMsg["repository"]["absolute_url"])

        commitMessages = []

        for cmt in dictMsg["commits"]:
            cmtLink = "<%scommits/%s|%s>" % (repoUrlRoot, cmt["raw_node"], cmt["node"])
            commitMessages.append("%s - %s" % (cmtLink, cmt["message"]))

        payload["text"] = "%s %s commit/s pushed to %s\n\n%s" % (userLink, commitCount, repoURL, "\n".join(commitMessages))

        req = requests.post(SLACK_INCOMING_WEB_HOOK, json.dumps(payload), headers={'content-type': 'application/json'})

class SlackWebHookResource(object):

    def on_post(self, req, res):
        res.status = falcon.HTTP_200
        param_str = ", ".join(req.params["payload"])

        dMsg = {}
        try:
            dMsg = json.loads(param_str)
        except:
            pass

        send_slack_message(dMsg)

        res.body = "ok"

if __name__ == "__main__":

    falcon_app = falcon.API()
    falcon_app.add_route("/", SlackWebHookResource())

    test_server = simple_server.make_server(SLACK_WEB_HOOK_HOST, SLACK_WEB_HOOK_PORT, falcon_app)
    print "\nServer starting..."
    print "Server Host: %s" % SLACK_WEB_HOOK_HOST
    print "Server Port: %s" % SLACK_WEB_HOOK_PORT

    try:
        test_server.serve_forever()
    except KeyboardInterrupt:
        print "\nApplication Terminated...\n"
