#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014 ko-zu <causeless@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os,sys
from subprocess import Popen, PIPE, STDOUT
import socket
from socket import AF_INET, AF_INET6, SOCK_DGRAM
import unittest


if "-s" in sys.argv or "--sudo" in sys.argv:
    SUDO = ["/usr/bin/sudo"]
else:
    SUDO = []

CAT = "/bin/cat"

IPTABLES = "/sbin/iptables"
PING = "/bin/ping"

IP6TABLES = "/sbin/ip6tables"
PING6 = "/bin/ping6"

LOCALHOST = "127.0.0.1"
LOCALPORT = 33434 + 1

DUMMYHOST = "192.0.2.1"


class TempRule(object):
    def __init__(self, iptables_path, rule):
        self.iptables_path = iptables_path
        self.rule = rule
        self.returncode = 0
        self.stdout = None
        self.stderr = None

    def __enter__(self):
        args = SUDO + [self.iptables_path, "-I"] + self.rule
        p = Popen(args, stdout=PIPE, stderr=PIPE)
        self.stdout, self.stderr = p.communicate()
        self.returncode = p.returncode
        return self

    def __exit__(self, *args):
        args = SUDO + [self.iptables_path, "-D"] + self.rule
        p = Popen(args, stdout=PIPE, stderr=PIPE)
        p.communicate()



class IPv4InfoMixin(object):
    
    iptables_path = IPTABLES
    ping_path     = PING

    localhost     = LOCALHOST
    localport     = str(LOCALPORT)

    localhost_long = LOCALHOST

    dummyhost     = "192.0.2.1"

    ipv6          = False
    
    inet          = socket.AF_INET
    icmp          = "icmp"


class IPv6InfoMixin(object):
    iptables_path = IP6TABLES
    ping_path     = PING6

    localhost     = "::1"
    localport     = str(LOCALPORT)

    localhost_long = "0000:0000:0000:0000:0000:0000:0000:0001"

    dummyhost     = "2001:db8::dead"

    ipv6          = True

    inet          = socket.AF_INET6
    icmp          = "icmpv6"



class IPTTestsBase(unittest.TestCase):
    
    @property
    def dummyrule(self):
        return ["INPUT", "-i", "lo", "-s", self.dummyhost, "-d", self.dummyhost] 

    @property
    def lorule(self):
        return ["INPUT", "-i", "lo", "-s", self.localhost, "-d", self.localhost]

    @property
    def loudprule(self):
        return self.lorule + ["-p", "udp", "--dport", self.localport]

    @property
    def lotcprule(self):
        return self.lorule + ["-p", "tcp", "--dport", self.localport]


    def sendudp(self):
        try:
            s = socket.socket(self.inet, SOCK_DGRAM)
            s.sendto("IPTTEST", (self.localhost, int(self.localport)))
            s.close()
        except socket.error:
            if s:
                s.close()
            raise


    def sendping(self):
        args = [self.ping_path] + "-q -c 1 -w 1".split() + [self.localhost]
        p = Popen(args, stdout=PIPE, stderr=PIPE)
        o, e = p.communicate()


    def sendtcp(self):
        try:
            s = socket.socket(self.inet)
            s.settimeout(0.5)
            s.connect( (self.localhost, int(self.localport)) )
            s.close()
        except socket.error:
            if s:
                s.close()

    def temprule(self, rule):
        return TempRule(self.iptables_path, rule)



    def validate(self, rule, proto="udp", func=None):
        with self.temprule(self.dummyrule):
            with self.temprule(rule) as p:
                self.assertEqual(0, p.returncode, "failed loading: -I "+" ".join(rule))

                if proto == "udp":
                    self.sendudp()
                elif proto == "tcp":
                    self.sendtcp()
                else:
                    self.sendping()
    
                args = SUDO + [self.iptables_path, "-vnxL", "INPUT", "1"]
                p = Popen(args, stdout=PIPE, stderr=PIPE)
                o, e = p.communicate()
                if p.returncode != 0:
                    raise self.failureException("failed to list iptables: " + " ".join(args()))
               
                self.assertTrue(long(o.split()[0]) > 0, "Rule is not counting: " + o)
                
                if func:
                    func(self)


    def test_length_module(self):
        rule = self.loudprule + "-m length --length=0:1500".split()
        self.validate(rule)


    def test_multiport_module(self):
        rule = self.loudprule + "-m multiport --dports".split() + [self.localport]
        self.validate(rule)


    def test_state_module(self):
        rule = self.loudprule + "-m state --state NEW".split()
        self.validate(rule)


    def test_string_module(self):
        rule = self.loudprule + "-m string --string IPTTEST --algo bm".split()
        self.validate(rule)


    def test_recent_module(self):
        rule = self.loudprule + "-m recent --name IPTTEST --set --rdest".split()

        def f(self):
            p = Popen(SUDO + [CAT, "/proc/net/xt_recent/IPTTEST"], stdout=PIPE, stderr=PIPE)
            o, e = p.communicate()

            self.assertTrue(self.localhost_long in o, o)

        self.validate(rule, func=f)


    def test_tcp_module(self):
        self.validate(self.lotcprule, proto="tcp")


    def test_udp_module(self):
        self.validate(self.loudprule, proto="udp")


    def test_limit_module(self):
        rule = self.loudprule + "-m limit --limit 10/second".split()
        self.validate(rule)

    
    def test_hashlimit_module(self):
        rule = self.loudprule + "-m hashlimit --hashlimit-name IPTTEST --hashlimit-mode dstip --hashlimit-upto 10/second --hashlimit-htable-expire 10000".split()
        self.validate(rule)

        def f(self):
            s = ""
            if os.path.exists("/proc/net/ipt_hashlimit/IPTTEST"):
                p = Popen(SUDO + [CAT, "/proc/net/ipt_hashlimit/IPTTEST"], stdout=PIPE, stderr=PIPE)
                o, e = p.communicate()
                s += o
            if os.path.exists("/proc/net/ip6t_hashlimit/IPTTEST"):
                p = Popen(SUDO + [CAT, "/proc/net/ip6t_hashlimit/IPTTEST"], stdout=PIPE, stderr=PIPE)
                o, e = p.communicate()
                s += o
            
            self.assertTrue(self.localhost_long in s, s)

        self.validate(rule, func=f)


    def test_mark_module(self):
        rule = self.loudprule + "-m mark ! --mark 1/1".split()
        self.validate(rule)


    def test_u32_module(self):
        rule = self.loudprule + "-m u32 --u32".split() + ["0 & 0xFFFF = 0x0:0xFFFF"]
        self.validate(rule)

    def test_LOG_target(self):
        rule = self.loudprule + "-j LOG --log-level debug --log-prefix IPTTEST".split()
        self.validate(rule)

    def test_MARK_target(self):
        rule = self.loudprule + "-j MARK --or-mark 0".split()
        self.validate(rule)



class IPTTests(IPTTestsBase, IPv4InfoMixin):

    def test_ttl_module(self):
        rule = self.loudprule + "-m ttl --ttl-gt 1".split()
        self.validate(rule)

    def test_icmp_module(self):
        rule = self.lorule + "-p icmp -m icmp --icmp-type echo-request".split()
        self.validate(rule, proto="icmp")




class IP6TTests(IPTTestsBase, IPv6InfoMixin):

    def test_hl_module(self):
        rule = self.loudprule + "-m hl --hl-gt 1".split()
        self.validate(rule)

    def test_icmpv6_module(self):
        rule = self.lorule + "-p icmpv6 -m icmpv6 --icmpv6-type echo-request".split()
        self.validate(rule, proto="icmp")



class Result(unittest.TestResult):

    def _str(self, test):
        if isinstance(test, IPTTests):
            f = "IPv4"
        else:
            f = "IPv6"
        return "{0} {1}".format(f, " ".join(test._testMethodName.split("_")[1:]))

    def addSuccess(self, test):
        if "-i" in  sys.argv:
            print self._str(test)

    def addFailure(self, test, err):
        if "-i" not in  sys.argv:
            print self._str(test), err[1]




if __name__ == '__main__':

    res = Result()
    unittest.TestLoader().loadTestsFromTestCase(IPTTests).run(res)
    if socket.has_ipv6:
        unittest.TestLoader().loadTestsFromTestCase(IP6TTests).run(res)
    sys.exit()






