#!/usr/bin/env python2
# -*- coding:utf8 -*-

'''
* forked from dnspod's offical python script for dynamic dns record
* modified by Justin Wong <bigeagle(at)xdlinux(dot)info>
* LICENSE: MIT License
'''

import httplib, urllib
import socket
import argparse
import time
import fcntl
import struct
import os, stat
import ConfigParser
import json
from getpass import getpass

DEBUG = False
VERBOSE = False
g_params = dict(
    login_email="", 
    login_password="", 
    format="json",
    domain_id=None, 
    record_id=None, 
    sub_domain="", 
    record_type="A",
    ttl=600,
    record_line="默认",
)

#domains to be updated
domains = []

interval = 300
interface = None
interactive = False

class Domain():
    def __init__(self,iface=None,domain=None,domain_id=None,sub_domain=None,record_id=None):
        self.iface = iface
        self.domain = domain
        self.domain_id = domain_id
        self.sub_domain = sub_domain
        self.record_id = record_id
    
    def gen_dict(self):
        self.dict = dict(
            domain_id=self.domain_id,
            sub_domain=self.sub_domain,
            record_id=self.record_id
        )

    def isComplete(self):
        return self.domain_id and self.sub_domain and self.record_id

    def get_domain_id(self):
        keys = ["login_email", "login_password", "format"]
        _param = { k:v for k,v in g_params.iteritems() if k in keys }
        domain_name = self.domain
        if domain_name == None:
            raise Exception("No domain name specified.")

        headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/json"}
        conn = httplib.HTTPSConnection("dnsapi.cn")
        conn.request("POST", "/Domain.list", urllib.urlencode(_param), headers)
        response = conn.getresponse()
        id = None
        rep = json.load(response)
        for domain in  rep['domains']:
            if domain['name'] == domain_name:
                id = domain['id']        
        conn.close()
        if id:
            if DEBUG: print id
            self.domain_id = id
        else:
            raise Exception("Record '"+domain_name+"' not found!")

    def get_record_id(self):
        keys = ["login_email", "login_password", "format"]
        _param = { k:v for k,v in g_params.iteritems() if k in keys }
        _param['domain_id'] = self.domain_id
        subdomain = self.sub_domain
        if subdomain==None:
            raise Exception("No subdomain specified.")
        if self.record_id:
            return
        headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/json"}
        conn = httplib.HTTPSConnection("dnsapi.cn")
        conn.request("POST", "/Record.List", urllib.urlencode(_param), headers)
        response = conn.getresponse()
        id = None
        rep = json.load(response)
        for record in  rep['records']:
            #if DEBUG: print record.find("name").text
            if record['name'] == subdomain:
                if DEBUG: print "Found", record['name']
                if id:
                    print rep['records'] 
                    raise Exception("Multipule records of '"+subdomain+"' found. Please specify record id! ")
                id = record['id']
        conn.close()
        if id:
            if DEBUG: print id
            self.record_id = id 
        else:
            raise Exception("Record '"+subdomain+"' not found!")

dict_merge = lambda a,b :dict( a.items() + b.items() ) 

def ddns(ip,params):
    params.update(dict(value=ip))
    if DEBUG: print params
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/json"}
    conn = httplib.HTTPSConnection("dnsapi.cn")
    conn.request("POST", "/Record.Modify", urllib.urlencode(params), headers)
    
    response = conn.getresponse()
    if DEBUG: print response.status, response.reason
    data = response.read()
    if DEBUG: print data
    conn.close()
    return response.status == 200


def get_current_ip(params):
    """get current ip of """
    keys = ["login_email", "login_password", "domain_id","format"]
    record_id = params['record_id']
    _param = { k:v for k,v in params.iteritems() if k in keys }
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/json"}
    conn = httplib.HTTPSConnection("dnsapi.cn")
    conn.request("POST", "/Record.List", urllib.urlencode(_param), headers)
    response = conn.getresponse()
    rep = json.load(response) 
    cur_ip = None
    for record in  rep["records"]:
        if record['id'] == record_id:
            cur_ip = record['value']
    conn.close()
    return cur_ip

def get_public_ip():
    """ get ip address from dnspod """
    if DEBUG: print "getting ip address from dnspod..."
    sock = socket.create_connection(('ns1.dnspod.net', 6666))
    ip = sock.recv(16)
    sock.close()
    return ip

def get_if_ip(ifname):
    """Get ip address by interface, Linux ONLY"""
    if DEBUG: print "getting ip address of", ifname
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', ifname[:15])
            )[20:24])

def getip(ifname):
    if ifname:
        return get_if_ip(ifname)
    else:
        return get_public_ip()

def create_config(fp,d):
    config = ConfigParser.RawConfigParser()
    config.add_section('general')
    config.set('general','login_email', g_params['login_email'])
    config.set('general','login_password',g_params['login_password'])
    config.set('general','interval','300')
    config.set('general','interactive','False')
    config.set('general','debug','False')
    
    d_sec = d.sub_domain+'.'+d.domain
    config.add_section(d_sec)
    config.set(d_sec,'record',d.sub_domain)
    config.set(d_sec,'record_id',d.record_id)
    config.set(d_sec,'enabled','True')
    config.set(d_sec,'iface',d.iface or '')
    config.write(fp)

def parse_config(fp):
    config = ConfigParser.RawConfigParser()
    config.readfp(fp)
    
    cfg = {}
    cfg['email'] = config.get('general','login_email')
    cfg['password'] = config.get('general','login_password')
    cfg['interval'] = config.getint('general','interval')
    cfg['debug'] = config.getboolean('general','debug')
    cfg['interactive'] = config.getboolean('general','interactive')
    
    domains = config.sections()[1:]
    if DEBUG: print domains
    cfg['domains']=[]
    for d in domains:
        cfg['domains'].append({
            'domain':str.join('.',d.split('.')[1:]),
            'record':config.get(d,'record'),
            'record_id':config.get(d,'record_id'),
            'enabled':config.getboolean(d,'enabled'),
            'iface':config.get(d,'iface'),
        })
    return cfg

def parse_arg():
    parser = argparse.ArgumentParser(description="Update dns record on dnspod dynamically.")
    parser.add_argument( '-I', '--interval', help="Set test interval, default is 300 seconds." )
    parser.add_argument( '-i', '--interface', help="Set interface." )
    parser.add_argument( '-u','--username', help="Set login email." )
    parser.add_argument( '-p','--password', help="Set login password." )
    parser.add_argument( '-d','--domain', help="Set domain name." )
    parser.add_argument( '-s','-r','--subdomain', help="Set subdomain/record name." )
    parser.add_argument( '--domain-id', help="Set domain id." )
    parser.add_argument( '--record-id', help="Set record id." )
    parser.add_argument( '--interactive', action="store_true", help="Set params interactively." )
    parser.add_argument( '--debug',action="store_true", help="Show debug outputs." )
    parser.add_argument( '-v','--verbose',action="store_true", help="Show more information." )
    return parser.parse_args()

def init():
    global DEBUG,interval,VERBOSE
    args = parse_arg()
    rcfile = os.path.expanduser('~/.dnspodrc')
    
    DEBUG = args.debug
    
    #default config
    cfg = dict(
        debug=False,
        interval=300,
        interactive=True,
        email=None,
        password=None,
    )

    #read config file
    if os.path.isfile(rcfile):
        mode = stat.S_IREAD|stat.S_IWRITE
        filemode = stat.S_IMODE(os.stat(rcfile).st_mode)
        if filemode != mode:
            raise Exception("Config file permission must be set to '600'")
        with open(rcfile,'r') as fp:
            cfg = parse_config(fp)
        first_run = False
    else:
        first_run = True
    
    # confiure
    DEBUG = args.debug or cfg['debug']
    if DEBUG:
        print "cfg:",cfg
    VERBOSE = args.verbose or DEBUG

    interval = args.interval or cfg['interval']
    interactive = args.interactive or cfg['interactive']
    
    #Login info
    if interactive:
        g_params['login_email'] = args.username or \
                raw_input("E-mail: ") or cfg['email'] 
        g_params['login_password'] = args.password or \
                getpass() or cfg['password'] 
    else:
        g_params['login_email'] = args.username or cfg['email'] 
        g_params['login_password'] = args.password or cfg['password']
    
    d = Domain()
    #domain and record id
    if args.domain_id:
        d.domain_id = args.domain_id 
    elif args.domain:
        d.domain = args.domain
        d.get_domain_id()
    elif interactive:
        d.domain= raw_input("Domain name: ")
        d.get_domain_id()

    if args.record_id:
        d.sub_domain = args.subdomain
        d.record_id = args.record_id
    elif args.subdomain:
        d.sub_domain = args.subdomain
        d.get_record_id() 
    elif interactive:
        d.sub_domain = raw_input("Subdomain: ")
        d.get_record_id() 
    
    if args.interface:
        d.iface = args.interface
    
    if first_run:
        with open(rcfile,'wb') as fp:
            print rcfile
            create_config(fp,d)
        os.chmod(rcfile,stat.S_IREAD|stat.S_IWRITE ) #chmod to 600 for password
        print "Config file created as " + rcfile

    if d.isComplete():
        d.gen_dict()
        domains.append(d)
        return

    # read from cfg
    for dd in cfg['domains']:
        if dd['enabled']:
            d = Domain(
                domain=dd['domain'],
                iface=dd['iface'],
                sub_domain=dd['record'],
                record_id=dd['record_id'] 
            )
            d.get_domain_id()
            d.get_record_id()
            d.gen_dict()
            domains.append(d)

def main():
    init()
    while True:
        try:
            for d in domains:
                params = dict_merge(g_params,d.dict)
                if DEBUG: print params
                
                current_ip = get_current_ip(params)
                ip = getip(d.iface)

                if VERBOSE:
                    print "domain_name: ", params['sub_domain']+'.'+d.domain
                    print "domain id:", params['domain_id']
                    print "record id:", params['record_id']
                    print "ip:", ip
                    print "record ip:", current_ip
                    print "interval: ", interval
                
                if current_ip != ip:
                    if ddns(ip,params):
                        current_ip = ip

        except Exception, e:
            print e
        time.sleep(interval)

if __name__ == '__main__':
    main()
