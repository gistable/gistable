#!/usr/bin/env python
"""
This takes a recipient email address and a graphite URL and sends a 
POST to <graphite host>/dashboard/email with a body that looks like
this: 

    sender=user%40example.com&recipients=user2%40example.com&subject=foo&message=bar&graph_params=%7B%22target%22%3A%22target%3DdrawAsInfinite(metric.path.in.graphite)%22%2C%22from%22%3A%22-2hours%22%2C%22until%22%3A%22now%22%2C%22width%22%3A600%2C%22height%22%3A250%7D

...which will cause the graphite installation to send an email.

This script will also ping graphite so that you can 
actually graph when these notifications were sent out as events, and 
layer those graphs on top of the graphs that correspond to the notification 
event, so we can visually verify that the alerts are going out (or attempted), 
and that it's happening at the right time, etc.

Note that the pingback functionality sends the events to a metric in graphite 
named 'nagios.<metricname>'. 

"""
import requests
import logging
from socket import socket
import time
import sys
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from optparse import OptionParser


CARBON_SERVER = 'host.name.fqdn'
CARBON_PORT = 2003

logging.basicConfig(filename='/var/log/sendgraph.log', level=logging.DEBUG)


def send_graph_email(graph, subject, sender, receivers, body=None):
    """
    Builds an email with the attached graph.

    :param body: Text portion of the alert notification email. 
    :param graph: Assumed to be a PNG, currently.
    :param subject: Email subject line
    :param sender: an email address
    :param receivers: list of email addresses to send to.
    :return:
    """
    logging.debug("body: %s  subject: %s  sender: %s  receivers: %s" % (body, subject, sender, receivers))
    if body is None:
        body = '\n'

    msg = MIMEMultipart()
    msg.attach(MIMEText(body))

    imgpart = MIMEImage(graph, _subtype='png')
    imgpart.add_header('Content-Disposition', 'attachment', filename='graph.png')
    msg.attach(imgpart)

    msg['to'] = ', '.join(receivers)
    msg['from'] = sender
    msg['subject'] = subject
    s = smtplib.SMTP()
    try:
        s.connect()
        s.sendmail(sender, receivers, msg.as_string())
        s.close()
    except Exception as out:
        logging.error("Sending mail failed: %s" % out)

def ping_graphite(metric_name):
    sock = socket()
    try:
        sock.connect( (CARBON_SERVER,CARBON_PORT) )
    except:
        print "Couldn't connect to %(server)s on port %(port)d, is carbon-agent.py running?" % { 'server':CARBON_SERVER, 'port':CARBON_PORT }
        sys.exit(1)

    now = time.time()
    message = '%s %s %s\n' % (metric_name, '1.0', now)
    try:
        sock.sendall(message)
    except Exception as out:
        logging.error("Updating graphite failed: %s", out)
        sys.exit(1)

    logging.info("Updated graphite: %s", message)

def do_options():
    parser = OptionParser()
    parser.add_option('-u', '--url',
                      action='store',
                      dest='graph_url',
                      help="URL to the graphite graph that spawned the nagios alert")
    parser.add_option('-t', '--to',
                      action='store',
                      dest = 'recip',
                      help='Email address of the alert recipient.')
    parser.add_option('-n', '--name',
                      action='store',
                      dest='alertname',
                      help='The $SERVICENAME$ or $HOSTNAME$ from nagios.')
    parser.add_option('-s', '--state',
                      action='store',
                      dest='state',
                      help='The $SERVICESTATE$ or $HOSTSTATE$ from nagios.')

    options, args = parser.parse_args()
    return options

def main():
    options = do_options()
    graph_url = options.graph_url
    logging.debug('graph url is %s' % graph_url)
    alertname = options.alertname
    state = options.state
    metric_name = '%s.%s.%s' % ('nagios', alertname.replace(' ', '_'), state)
    subject = '%s: %s' % (state, alertname)
    sender = 'graphalert@example.com'
    receivers = options.recip.split(' ')
    graph = requests.get(graph_url)
    logging.debug("Response headers for graph request: %s", graph.headers)
    body = "According to graphite, %s is in a %s state. Here's a graph. Check it out." % (alertname, state)
    send_graph_email(graph.content, subject, sender, receivers, body)
    logging.debug("Mail sent - pinging graphite now...")
    ping_graphite(metric_name)
    
if __name__ == '__main__':
    main()
