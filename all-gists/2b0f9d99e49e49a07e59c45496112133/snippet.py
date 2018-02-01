#!/usr/bin/env python2.7
# Requirements: pip install ari gevent
import argparse
import ari
import gevent
from gevent.monkey import patch_all; patch_all()
from gevent.event import Event
import logging
from requests.exceptions import HTTPError, ConnectionError
import socket
import time

logging.basicConfig() # Important!
                      # Otherwise you get No handlers could be found for
                      # logger "ari.client"

ARI_URL = 'http://192.168.56.101:8088/ari'
ARI_USER = 'test'
ARI_PASSWORD = 'test'

client = ari.connect(ARI_URL, ARI_USER, ARI_PASSWORD)

def run():
    try:
        client.run('originator')
    except socket.error as e:
        if e.errno == 32: # Broken pipe as we close the client.
            pass
    except ValueError as e:
        if e.message == 'No JSON object could be decoded': # client.close()
            pass

def originate(endpoint=None, callerid=None, context=None, extension=None, 
              priority=None, timeout=None):
    # Go!
    evt = Event()  # Wait flag for origination
    result = {}
    gevent.sleep(0.1) # Hack to let run() arrange all.
    start_time = time.time()
    try:
        channel = client.channels.originate(
            endpoint=endpoint,
            callerId=callerid,
            app='originator',
            timeout=timeout
        )

        def state_change(channel, event):
            state = event['channel']['state']
            if state == 'Up':
                channel = channel.continueInDialplan(
                    context=context, extension=extension, priority=priority)

        def destroyed(channel, event):
            end_time = time.time()
            result['status'] = 'success'
            result['message'] = '%s (%s)' % (
                                    event.get('cause_txt'),
                                    event.get('cause'))
            result['duration'] = '%0.2f' % (end_time - start_time)
            evt.set()

        channel.on_event('ChannelDestroyed', destroyed)
        channel.on_event('ChannelStateChange', state_change)
        # Wait until we get origination result
        evt.wait()
        client.close()
        return

    except HTTPError as e:
        result['status'] = 'error'
        try:
            error = e.response.json().get('error')            
            result['message'] = e.response.json().get('error')
            
        except Exception:
            result['message'] = e.response.content        

    finally:
        print result
        client.close()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('endpoint', type=str, help='Endpoint, e.g. SIP/operator/123456789')
    parser.add_argument('callerid', type=str, help='CallerID, e.g. 111111')
    parser.add_argument('context', type=str, help='Asterisk context to connect call, e.g. default')
    parser.add_argument('extension', type=str, help='Context\'s extension, e.g. s')
    parser.add_argument('priority', type=str, help='Context\'s priority, e.g. 1')
    parser.add_argument('timeout', type=int, help='Originate timeout, e.g. 60')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    runner = gevent.spawn(run)
    originator = gevent.spawn(originate, endpoint=args.endpoint, callerid=args.callerid,
                     context=args.context, extension=args.extension, 
                     priority=args.priority, timeout=args.timeout
    )
    gevent.joinall([originator, runner])