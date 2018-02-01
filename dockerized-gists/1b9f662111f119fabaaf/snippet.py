# (c) 2015, Jan-Piet Mens <jpmens(at)gmail.com>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

from ansible import utils, errors
import socket
HAVE_DNS=False
try:
    import dns.resolver
    import dns.reversename
    from dns.exception import DNSException
    HAVE_DNS=True
except ImportError:
    pass

# ==============================================================
# DIG: DNS records
#
# --------------------------------------------------------------

class LookupModule(object):

    def __init__(self, basedir=None, **kwargs):
        self.basedir = basedir

        if HAVE_DNS == False:
            raise errors.AnsibleError("Can't LOOKUP(dig): module dns.resolver is not installed")

    def run(self, terms, inject=None, **kwargs):

        '''
        terms contains a string with things to `dig' for. We support the
        following formats:
            example.com                                     # A record
            example.com/TXT                                 # specific qtype
            192.168.1.2/PTR                                 # reverse PTR
              ^^ shortcut for 2.1.168.192.in-addr.arpa/PTR
            example.net/AAAA  @nameserver                   # query specified server
                               ^^^ can be comma-sep list of names/addresses
        '''
        terms = terms.split()

        # Create Resolver object so that we can set NS if necessary
        myres = dns.resolver.Resolver()

        domain = None
        qtype  = 'A'

        for t in terms:
            if t.startswith('@'):       # e.g. "@10.0.1.2,192.168.1.1" is ok.
                nsset = t[1:].split(',')
                nameservers = []
                for ns in nsset:
                    # Check if we have an IP address. If so, use that, otherwise
                    # resolve name to address using system's resolver
                    try:
                        socket.inet_aton(ns)
                        nameservers.append(ns)
                    except:
                        try:
                            nsaddr = dns.resolver.query(ns)[0].address
                            nameservers.append(nsaddr)
                        except Exception, e:
                            raise errors.AnsibleError("dns lookup NS: ", str(e))
                    myres.nameservers = nameservers
                continue
            if '/' in t:
                try:
                    domain, qtype = t.split('/')
                except:
                    domain = t.split('/')
            else:
                domain = t

        # print "--- domain = {0} qtype={1}".format(domain, qtype)

        ret = []

        if qtype.upper() == 'PTR':
            try:
                n = dns.reversename.from_address(domain)
                domain = n.to_text()
            except dns.exception.SyntaxError:
                pass
            except Exception, e:
                pass
                print "START"
                # raise errors.AnsibleError("dns.reversename unhandled exception", str(e))

        responses = []
        try:
            answers = myres.query(domain, qtype)
            for rdata in answers:
                s = rdata.to_text()
                if qtype.upper() == 'TXT':
                    s = s[1:-1]  # Strip outside quotes on TXT rdata
                responses.append(s)

        except dns.resolver.NXDOMAIN:
            responses.append('NXDOMAIN')
        except dns.resolver.NoAnswer:
            responses.append("")
        except dns.resolver.Timeout:
            responses.append('')
        except dns.exception.DNSException, e:
            raise errors.AnsibleError("dns.resolver unhandled exception", e)

        for r in responses:
            ret.append(r)
        return ret
