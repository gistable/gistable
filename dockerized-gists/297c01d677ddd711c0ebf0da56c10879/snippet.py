#import gevent
#from ghost import Ghost, Session
import requests
import re
import json
import time
import socket
#from gevent import monkey; monkey.patch_all()
timeout = 90
socket.setdefaulttimeout(timeout)
#from ghost import Ghost
#ghost = Ghost()

class toolCli(object):

    def __init__(self):
        pass

    @staticmethod
    def check_port(addr, port, retry=3):
        while True:
            r = requests.get('http://120.26.91.33:5000/check?ip=%s&port=%s' % (addr, port), timeout=10)
            if 'bad' in r:
                if retry > 0:
                    retry -= 1
                    continue
                return False
            return True


class OpCli(object):

    def __init__(self, cookie):
        self.session = requests.session()
        self.session.headers['user-agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
        self.h = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
        self.cookie = cookie
        self.session.headers['cookie'] = cookie

    def manage(self, vm_id):
        r = self.session.get('https://panel.op-net.com/onecloud/%s/manage' % vm_id)
        if 'IP: </b>' not in r.text:
            return None
        return {
            'ip': re.search('IP: </b>([\d.]+)', r.text).group(1),
            'csrf_token': re.search('"([a-z0-9]{40})"', r.text).group(1)
        }

    def destroy(self, vm_id, csrf_token):
        data = {
            'server_id': vm_id,
            'action': 'destroy_vm',
            'csrf_token': csrf_token
        }
        r = self.session.post('https://panel.op-net.com/src/onecloud_manager.php', data)
        return 'success' in r.text

    def open(self, vm_id, plan='Plan 01', location='14', os='linux-ubuntu-16.04-server-x86_64-min-gen2-v1'):
        # get csrf_token
        data = {
            'x': 25,
            'y': 21,
            'vm_id': vm_id
        }
        r = self.session.post('https://panel.op-net.com/cloud/open', data, timeout=timeout)
        r = re.search('"([a-z0-9]{40})"', r.text)
        if not r:
            raise Exception('open vm error: fetch token failed.')
        # create vm
        data = {
            'plan': plan,
            'location': location,
            'os': os,
            'vm_id': vm_id,
            'hostname': 'a.b.c',
            'root': '',
            'csrf_token': r.group(1)
        }
        r = self.session.post('https://panel.op-net.com/cloud/open', data, timeout=timeout, allow_redirects=False)
        if r.status_code != 302:
            r = re.search('class="message error">([\S\s]+)?</h4>', r.text)
            if not r:
                raise Exception('open vm error: unknow reason.')
            raise Exception('open vm error: %s' % r.group(1).strip())



######################################
vm_id = '70550'
plan = 'Plan 01'
location = '13'
cookie = 'id=0b52a5ab6c1969a254597047ce; _gat=1; _ga=GA1.2.2084353983.1511673858; _gid=GA1.2.496062921.1511794137; tz=8'
######################################
done = False
if toolCli.check_port('58.222.18.30', 80) is not True: print('tool api test failed')

def buybuybuy(tid):
    cli = OpCli(cookie)
    t = 3
    global done
    while True:
        try:
            if done:
                return
            print('check vm')
            m = cli.manage(vm_id)
            if m:
                # if vm created
                print('tid %s vm already created ip:%s' % (tid, m['ip']))
                if not toolCli.check_port(m['ip'], 22):
                    # ip block
                    print('vm ip:%s blocked begin destroy ...' % m['ip'])
                    cli.destroy(vm_id, m['csrf_token'])
                    time.sleep(30)
                    continue
                print('vm created success and ip not block by gfw.')
                done = True
                return
            print('tid %s vm open ...' % tid)
            cli.open(vm_id, plan=plan, location=location)
            print('vm open successed wait vm init.')            # open success wait created
            time.sleep(2 * 60)
        except Exception as e:
             time.sleep(60)
             while True:
                try:
                    time.sleep(10)
                    #cli.bypass2()
                    break
                except:
                    time.sleep(60)

buybuybuy(1)
#gevent.joinall([gevent.spawn(buybuybuy, i) for i in range(1)])