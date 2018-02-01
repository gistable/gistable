def make_rules(hosts, ports, proto):
    return [{"proto": proto,
             "from_port": port,
             "to_port": port,
             "cidr_ip": host} for host in hosts for port in map(int, ports.split(","))]

class FilterModule(object):
     def filters(self):
         return {'make_rules': make_rules}


usage:

random_hosts:
  - 192.168.1.2/32
  - 172.16.0.2/32

ec2_group:
  rules: "{{ random_hosts | make_rules('22,8080', 'tcp') }}"