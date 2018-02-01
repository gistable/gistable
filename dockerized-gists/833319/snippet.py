'''
Copyright (c) 2011, Richard Nienaber
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
The name of 'Richard Nienaber' may not be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Dependencies:
ldap - http://pypi.python.org/pypi/python-ldap/
graphviz - http://www.graphviz.org/Download_windows.php
pydot - pip install pydot
'''

import argparse
import ldap
import re
from pydot import Dot, Node, Edge


class LdapSearcher(object):
    def __init__(self, server, partDomain, user, password):
        l = ldap.initialize(server)
        l.set_option(ldap.OPT_REFERRALS, 0)
        l.protocol_version = 3
        l.simple_bind_s(user, password)

        self.ldap = l
        self.scope = ldap.SCOPE_SUBTREE
        self.attributes = ['directReports', 'displayName', 'title']
        self.partDomain = partDomain

    def search(self, base, filter=None):
        return self.ldap.search_s(base, self.scope, filter, self.attributes)

    def search_by_accountName(self, base, name):
        filter = '(&(objectClass=user)(sAMAccountName=' + name + '))'
        return self.search(base, filter)

    def retrieve_hierarchy(self, rootUserName, maxDepth):
        root = self.search_by_accountName(self.partDomain, rootUserName)
        rootName = self.getName(root)

        visited = set([])
        reports = {}
        self.recurse_direct_reports(root, visited, reports, 0, maxDepth)
        return rootName, reports

    def getName(self, entry):
        attributes = entry[0][1]
        title = '' if not 'title' in attributes else attributes['title'][0]
        return (attributes['displayName'][0], title)

    def recurse_direct_reports(self, entry, visited, reports, depth, maxDepth):
        if depth == maxDepth:
            return
        dn, properties = entry[0]
        if dn in visited:
            return

        visited.add(dn)

        if not 'directReports' in properties:
            return

        name = self.getName(entry)
        reports[name] = []

        for report in properties['directReports']:
            reportEntry = self.search(report, '(objectClass=*)')
            reports[name].append(self.getName(reportEntry))
            self.recurse_direct_reports(reportEntry, visited, reports, depth + 1, maxDepth)


def render_graph(root, hierarchy, args):
    g = Dot()
    g.set_root(root[0])

    for manager in hierarchy:
        g.add_node(Node(manager[0], shape='box'))
        for subordinate in hierarchy[manager]:
            g.add_node(Node(subordinate[0], shape='box'))
            g.add_edge(Edge(manager[0], subordinate[0]))

    g.write_svg(args.file, args.imageType, args.layout)


def main(args):
    #Doing something a bit silly here, you may have to tweak it
    domain = re.search('ldap://((.*\.?)+)', args.server)
    split = domain.groups()[0].split('.')[1:]
    partDomain = 'dc=' + ',dc='.join(split)

    print ''
    print 'Creating hierarchy...'
    searcher = LdapSearcher(args.server, partDomain, args.user, args.password)
    root, hierarchy = searcher.retrieve_hierarchy(args.root, args.depth)

    print 'Rendering graph...'
    render_graph(root, hierarchy, args)
    print 'Completed'

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', '-s', help='The FQDN of the ldap server e.g. ldap://domain.server.com', required=True)
    parser.add_argument('--user', '-u', help='The user to log into the ldap server with e.g. user@domain.server.com', required=True)
    parser.add_argument('--password', '-p', help='The password of the user to use to login into the ldap server', required=True)
    parser.add_argument('--root', '-r', help='The root user''s login name e.g. name.surname', required=True)
    parser.add_argument('--file', '-f', help='The file to output to e.g. c:\chart.png', required=True)
    parser.add_argument('--depth', '-d', type=int, default=max, help='The amount of levels to represent in the hierarchy.')
    parser.add_argument('--imageType', '-i', help='An image type understood by GraphViz e.g. png, svg, etc.')
    parser.add_argument('--layout', '-l', help='A layout type understood by GraphViz e.g. dot, neato, circo, etc.')

    args = parser.parse_args()
    main(args)
