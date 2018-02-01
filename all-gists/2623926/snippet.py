from dns.resolver import Resolver

# make a system resolver using /etc/resolv.conf
sys_r = Resolver()
dns = ['ns1.dreamhost.com', 'ns2.dreamhost.com', 'ns3.dreamhost.com']

dreamhost_dns = [ item.address for server in dns for item in sys_r.query(server) ]

# a resolver using dreamhost dns server
dreamhost_r = Resolver()
dreamhost_r.nameservers = dreamhost_dns

answer = dreamhost_r.query('slobodensoftver.org.mk', 'mx')

for mx in answer.rrset.items:
    print mx

