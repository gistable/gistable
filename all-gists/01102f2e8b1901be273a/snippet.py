#!/bin/python3
import requests
import re
import os
import requests
import json

def getIp():
    s = os.popen('ssh root@192.168.1.1 ifconfig').read()
    ip = re.search(r'eth0.2[\w\W]+?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', s).groups()[0]
    return ip

def checkifchange(n):
    if os.path.exists('/home/pan/bin/ip'):
        with open('/home/pan/bin/ip') as fp:
            a = fp.read().strip()
    else:
        a = ''
    if n == a:
        return False
    else:
        with open('/home/pan/bin/ip','w') as fp:
            fp.write(n)
        return True

def updateIP(n):
    r = requests.Session()
    r.headers['User-Agent'] = 'pandada8Updater/0.1-Alpha (pandada8@gmail.com)'
    token = 'token'
    domain = "ddns.example.com"
    if len(domain.split(".")) == 2:
        main = domain
        sub = "@"
    else:
        main = ".".join(domain.split(".")[-2:])
        sub = domain.replace("." + main, "")

    # Get domains
    domains = r.post('https://dnsapi.cn/Domain.List',data = {"login_token": token, 'format':'json'}).json()
    domain_id = [i['id'] for i in domains['domains'] if i['name'] == main][0]

    # Get Record
    records = r.post('https://dnsapi.cn/Record.List',data = {'login_token': token, 'format':'json','domain_id':domain_id}).json()
    record = [i for i in records['records'] if i['name'] == sub and i['type'] == 'A'][0]
    if record['value'] != n:
        # modify the ip
        print('Original:{}'.format(record['value']))
        ret = r.post('https://dnsapi.cn/Record.Ddns',data = {'login_token':token,'format':'json','domain_id':domain_id,'record_id':record['id'],'value':n,'record_line':'默认','sub_domain':sub}).json()
        if int(ret['status']['code']) != 1:
            msg = "Error\n{}".format(json.dumps(ret,indent=4))
        else:
            msg = 'Succ\n{}'.format(json.dumps(ret,indent=4))
        print(msg)
    else:
        print('Not Change')

def main():
    n = getIp()
    print('Now ip:'+ n)
    if checkifchange(n):
        updateIP(n)


if __name__ == '__main__':
    main()
