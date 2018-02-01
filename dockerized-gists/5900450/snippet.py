# Add this to your fabfile.py (or import it from there)
from boto.ec2.connection import EC2Connection


class EC2Resolver(object):

    AWS_KEY_ID = 'xxxxxxx'
    AWS_SECRET_ACCESS_KEY = 'xxxxxx'  # Alternitavely take this info from environment variables or some other resource.

    def __init__(self):
        self.conn = EC2Connection(
            EC2Resolver.AWS_KEY_ID,
            EC2Resolver.AWS_SECRET_ACCESS_KEY
        )
        self._host_map = None

    def _generate_host_map(self):
        if self._host_map is None:
            self._host_map = {}
            for reservation in self.conn.get_all_instances():
                for instance in reservation.instances:
                    self._host_map[instance.tags.get('Name')] = instance.public_dns_name
        return self._host_map

    def generate_roledef(self, patterns):
        """
        Patterns - a mapping between role name and
        regular expression to match against. Example:
        {
            "db": "swayy-prod-db\d+",
            "web": "swayy-prod-web\d+",
            "worker": "swayy-prod-worker\d+",
            "python": "swayy-prod-(web|worker)\d+",  # Will match all web and worker servers
            "all": "swayy-prod-.*"  # Will match ALL production servers
        }
        """
        roledef = {}
        host_map = self._generate_host_map()
        for role, pattern in patterns.items():
            for name in host_map.keys():
                if re.match(pattern, name):
                    if not role in roledef:
                        roledef[role] = []
                    roledef[role].append(host_map[name])
        return roledef

# usage:
# Instantiate an EC2Resolver object, and replace existing roledefs with
# something like:
# >>> ec2_resolver.generate_roledef({'web': 'prod-.*'})