'''
Created on Mar 10, 2014

@author: jimhorng
'''

from apns import APNs, Payload
import time
import logging
import sys
import random

# Configurations
TOKEN_HEX = ''
TOKEN_HEX_BAD = ''
CERT_FILE = ''


USE_SANDBOX=True

_logger = logging.getLogger()
stream_handler = logging.StreamHandler(stream=sys.stdout)
file_handler = logging.FileHandler(filename='apns_test.log')
formatter = logging.Formatter('[%(asctime)s][%(process)s][%(threadName)s][%(pathname)s:%(lineno)d][%(levelname)s] %(message)s','%m-%d %H:%M:%S')
stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)
_logger.addHandler(stream_handler)
_logger.addHandler(file_handler)
_logger.setLevel(logging.DEBUG)

apns = APNs(use_sandbox=USE_SANDBOX, cert_file=CERT_FILE, enhanced=True)

import datetime
payload123 = {'aps': {
                   'badge': 9,
                   'alert': "jim:apns_test 123 " + str(datetime.datetime.now().isoformat()),
                   'sound': "default"
                   },
              'test_key1': "test123"
    }

def response_listener(error_response):
    _logger.debug("client get error-response: " + str(error_response))

def wait_till_error_response_unchanged():
    if hasattr(apns.gateway_server, '_is_resending'):
        delay=1
        count = 0
        while True:
            if apns.gateway_server._is_resending == False:
                time.sleep(delay)
                if apns.gateway_server._is_resending == False:
                    count = count + delay
                else: count = 0
            else: count = 0
            
            if count >= 10:
                break
        return delay * count
    return 0

def process(token, qty, send_interval=0, start_idx=1):
    payload = payload123.copy()
    base_alert = payload123['aps']['alert']
    apns.gateway_server.register_response_listener(response_listener)
    for i in range(start_idx, start_idx+qty):
        payload['aps']['alert'] = base_alert + str(i)
#         identifier = random.getrandbits(32)
        identifier = i        
        apns.gateway_server.send_notification(token, Payload(custom=payload), identifier=identifier)
        _logger.info("client sent to: " + str(identifier))
        
        _logger.debug("getting msg from feedback server...")
        for (token, failed_time) in apns.feedback_server.items():
            _logger.debug("failed: " + str(token) + "\tmsg: " + str(failed_time))
        
        time.sleep(send_interval)

def test_random_identifier(qty):
    payload = payload123.copy()
    for _ in range(qty):
        identifier = random.getrandbits(32)
        apns.gateway_server.send_notification(TOKEN_HEX, Payload(custom=payload), identifier=identifier)
        print "sent to ", identifier

def test_normal_fail():
    test_normal(qty=100, start_idx=1)
    test_fail(qty=1, start_idx=101)
    test_normal(qty=100, start_idx=102)
    test_fail(qty=2, start_idx=202)
    test_normal(qty=100, start_idx=204)
    
def test_normal(qty=1, send_interval=0, start_idx=1):
    process(TOKEN_HEX, qty=qty, send_interval=send_interval, start_idx=start_idx)

def test_fail(qty=1, send_interval=0, start_idx=1):
    process(TOKEN_HEX_BAD, qty=qty, send_interval=send_interval, start_idx=start_idx)

def test_fail_nonenhance(qty):
    global apns
    apns = APNs(use_sandbox=True, cert_file=CERT_FILE)
    process(TOKEN_HEX_BAD, qty=qty)

def test_normal_nonenhance(qty):
    global apns
    apns = APNs(use_sandbox=True, cert_file=CERT_FILE)
    process(TOKEN_HEX, qty=qty)

def test_send_interval(send_interval=0):
    for _ in xrange(100):
        
        _check_netstat()

        test_normal(5, send_interval)
        
        _check_netstat()
        
        time.sleep(60 * 130)

def test_send_by_signal():
    import signal
    signal.signal(signal.SIGUSR2, sig_handler_for_test_normal)
    
    while True:
        time.sleep(1)

def sig_handler_for_test_normal(signum, frame):
    _logger.debug('Signal handler called with signal:%s' % signum)
    import traceback
    _logger.debug("trackback:%s" % traceback.format_stack(frame))
    test_normal(2)

def _check_netstat():
    import subprocess
    cmd = """netstat -ant | grep 2195"""
    try:
        output = subprocess.check_output(cmd, shell=True)
    except Exception as e:
        output = str(e)
    _logger.debug("socket status: %s" % output)

def test_runner():
    test_normal(1000, 0)
    test_normal_fail()
    test_fail(1000, 0)  # fast fail
    test_fail(10, 1)  # slow fail
    test_fail(3, 40)  # fail after idle timeout
    test_fail_nonenhance(100)
    test_normal_nonenhance(100)
    test_random_identifier(1000)
    test_send_interval()
    test_send_by_signal()

def main():
#     time_start = time.time()
    
    test_runner()
    
    time.sleep(5)
    
#     delay = wait_till_error_response_unchanged()
#     apns.gateway_server.force_close()
#     time_end = time.time()
#     _logger.info("time elapsed: " + str(time_end - time_start - delay))
    
if __name__ == '__main__':
    main()