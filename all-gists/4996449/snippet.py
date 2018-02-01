#        DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE 
#                    Version 2, December 2004 

# Copyright (C) 2004 Sam Hocevar <sam@hocevar.net> 

# Everyone is permitted to copy and distribute verbatim or modified 
# copies of this license document, and changing it is allowed as long 
# as the name is changed. 

#            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE 
#   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION 

#  0. You just DO WHAT THE FUCK YOU WANT TO.

import urllib2
import json
from supervisor import childutils
import sys
import socket

 
class PagerDutyNotifier(object):
    def __init__(self, pd_service_key):
        self.pd_service_key = pd_service_key
        def run(self):
            while True:
                headers, payload = childutils.listener.wait()
                sys.stderr.write(str(headers) + '\n')
                payload = dict(v.split(':') for v in payload.split(' '))
                sys.stderr.write(str(payload) + '\n')
                if headers['eventname'] == 'PROCESS_STATE_EXITED' and not int(payload['expected']):
                    data = {'service_key': self.pd_service_key,
                            'event_type': 'trigger',
                            'description': '{} service has crashed unexpectedly on {}'.format(payload['processname'], socket.gethostname())
                    }
                    try:
                        res = urllib2.urlopen('https://events.pagerduty.com/generic/2010-04-15/create_event.json', json.dumps(data))
                    except urllib2.HTTPError, ex:
                        sys.stderr.write('{} - {}\n{}'.format(ex.code, ex.reason, ex.read()))
                    else:
                        sys.stderr.write('{}, {}\n'.format(res.code, res.msg))
                    childutils.listener.ok()
                    sys.stderr.flush()
    
if __name__ == '__main__':
    pager_duty_service_key = sys.argv[1]
    pager_duty_notifer = PagerDutyNotifier(pager_duty_service_key)
    pager_duty_notifer.run()

