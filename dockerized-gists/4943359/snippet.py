#!/usr/bin/env python
#-*- coding:utf8 -*-

# paramiko の ProxyCommandの Sample
# -------------------------------------------------
#
# ~/.ssh/config
#
#  Host proxy-server
#     User hoge
#     HostName proxy.example.com
#     IdentityFile ~/.ssh/id_rsa_proxy
#
#  Host dest-server
#     User fuga
#     HostName proxy.example.com
#     IdentityFile ~/.ssh/id_rsa_dest
#     ProxyCommand ssh proxy-server nc %h %p
#
# local -> proxy-server -> dest-server の流れでコマンドを実行したい
#
# see also https://github.com/paramiko/paramiko/pull/97

import paramiko
import sys
import os

def test_client(host_name):
    conf = paramiko.SSHConfig()
    conf.parse(open(os.path.expanduser('~/.ssh/config')))
    host = conf.lookup(host_name)
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        host['hostname'], username=host['user'],
        key_filename=host['identityfile'],
        sock=paramiko.ProxyCommand(host.get('proxycommand'))
    )
    stdin, stdout, stderr = client.exec_command('ls /home')
    print stdout.read()
    stdin, stdout, stderr = client.exec_command('ls /')
    print stdout.read()

if __name__ == '__main__':
    test_client("dest-server")
