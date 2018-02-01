import requests
import json
import sys
from collections import deque
from concurrent.futures import ThreadPoolExecutor as Pool
from datetime import datetime
from os import mkdir
from os.path import isdir

def debug(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

relevant_events = {'joined_channel', 'you_joined_channel', 'parted_channel',
                   'you_parted_channel', 'kicked_channel', 'you_kicked_channel',
                   'quit', 'quit_server', 'nickchange', 'you_nickchange',
                   'user_channel_mode', 'channel_mode', 'notice', 'buffer_msg',
                   'buffer_me_msg', 'channel_topic'}

program, email, password, dest = sys.argv

debug('authenticating as %s with password %s' % (email, password))

auth_response = requests.post(
    'https://www.irccloud.com/chat/login',
    data={
        'email': email,
        'password': password
    }
)
cookies = {'session': auth_response.json()['session']}
debug('authenticated: %r' % cookies)

initial_buffer_events = []
debug('getting stream' % cookies)
stream = requests.get('https://www.irccloud.com/chat/stream', cookies=cookies, stream=True)
for line in stream.iter_lines():
    message = json.loads(line.decode('utf-8'))
    debug('message: %s' % message['type'])
    if message['type'] == 'oob_include':
        debug('requesting buffers from %s' % message['url'])
        buffers = requests.get('https://www.irccloud.com' + message['url'], cookies=cookies)
        initial_buffer_events = buffers.json()
        break

class Connection:
    def __init__(self, name, id):
        self.name = name
        self.id = id
        self.channels = []
        self.queries = []
        self.console = None
    
    def add_buffer(self, buffer):
        if buffer.type == 'console':
            self.console = buffer
        elif buffer.type == 'channel':
            self.channels.append(buffer)
        elif buffer.type == 'conversation':
            self.queries.append(buffer)

class Buffer:
    def __init__(self, name, id, type, start_of_history=0):
        self.name = name
        self.id = id
        self.type = type
        self.start_of_history = start_of_history
        self.events = deque()
    
    def add_event(self, event):
        self.events.append(event)

if isinstance(initial_buffer_events, dict):
    debug(repr(initial_buffer_events))
    sys.exit()

connections = {}
buffers = {}
for event in initial_buffer_events:
    if event['type'] == 'makeserver':
        connections[event['cid']] = Connection(event['name'], event['cid'])
    elif event['type'] == 'makebuffer':
        buffer = Buffer(event['name'], event['bid'], event['buffer_type'], start_of_history=event['min_eid'])
        buffers[event['bid']] = buffer
        connections[event['cid']].add_buffer(buffer)
    elif event['type'] in relevant_events:
        buffers[event['bid']].add_event(event)

def fill_buffer(cid, buffer):
    buffer_events = True
    if len(buffer.events) > 0:
        beforeid = buffer.events[0]['eid']
    else:
        beforeid = None

    while buffer_events:
        debug('requesting events before %r on %r (%r) ...' % (beforeid, buffer.name, buffer.id))
        params = {
            'cid': cid,
            'bid': buffer.id,
            'num': 1000,
        }
        if beforeid: params['beforeid'] = beforeid
        buffer_events = requests.get(
            'https://www.irccloud.com/chat/backlog',
            params=params,
            cookies=cookies
        )
        try:
            buffer_events = buffer_events.json()
        except:
            continue
        for event in reversed(buffer_events):
            if event['type'] in relevant_events: buffer.events.appendleft(event)
        if buffer_events:
            beforeid = buffer_events[0]['eid']
        else:
            beforeid = 0
        if buffer.start_of_history == buffer.events[0]['eid']: buffer_events = []

for cid, connection in connections.items():
    pool = Pool(16)
    for x in pool.map(lambda buffer: fill_buffer(cid, buffer), connection.channels + connection.queries + [connection.console]):
        pass

for connection in connections.values():
    debug('writing logs for %r (cid %r)' % (connection.name, connection.id))
    cbase = '%s/%s' % (dest, connection.name)
    for buffer_type in ('channels', 'queries'):
        if not isdir(cbase): mkdir(cbase)
        if not isdir('%s/%s' % (cbase, buffer_type)): mkdir('%s/%s' % (cbase, buffer_type))
        for buffer in getattr(connection, buffer_type):
            debug('writing logs for %r (bid %r)' % (buffer.name, buffer.id))
            bbase = '%s/%s/%s' % (cbase, buffer_type, buffer.name)
            if not isdir(bbase): mkdir(bbase)
            for event in buffer.events:
                time = datetime.fromtimestamp(event['eid'] / 10 ** 6)
                with open('%s/%s.txt' % (bbase, time.strftime('%Y-%m-%d')), 'a', encoding='utf-8') as f:
                    def log(line):
                        print('%s %s' % (time.strftime('%H:%M:%S'), line), file=f)
                    if event['type'] in {'buffer_msg', 'notice'}:
                        log('<%s> %s' % (event['from'] if 'from' in event else event['server'], event['msg']))
                    elif event['type'] == 'buffer_me_msg':
                        log('* %s %s' % (event['from'] if 'from' in event else event['server'], event['msg']))
                    elif event['type'] in {'joined_channel', 'you_joined_channel'}:
                        log('*** %s (%s) has joined %s' % (event['nick'], event['hostmask'], event['chan']))
                    elif event['type'] in {'parted_channel', 'you_parted_channel'}:
                        log('*** %s (%s) has parted %s (%s)' % (event['nick'], event['hostmask'], event['chan'], event['msg']))
                    elif event['type'] in {'kicked_channel', 'you_kicked_channel'}:
                        log('*** %s kicked %s from %s (%s)' % (event['kicker'], event['nick'], event['chan'], event['msg']))
                    elif event['type'] in {'quit', 'quit_server'}:
                        log('*** %s has quit (%s)' % (event['nick'], event['msg']))
                    elif event['type'] in {'nickchange', 'you_nickchange'}:
                        log('*** %s is now known as %s' % (event['oldnick'], event['newnick']))
                    elif event['type'] == 'channel_mode':
                        log('*** %s sets mode %s' % (event['from'] if 'from' in event else event['server'], event['diff']))
                    elif event['type'] == 'user_channel_mode':
                        log('*** %s sets mode %s %s' % (event['from'] if 'from' in event else event['server'], event['diff'], event['nick']))
                    elif event['type'] == 'channel_topic':
                        log('*** %s changed the topic to: %s' % (event['author'], event['topic']))
