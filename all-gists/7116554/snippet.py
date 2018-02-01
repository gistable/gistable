# Get password from ~/.my.cnf if it exists
my_cnf_path = os.path.expanduser('~/.my.cnf')
if os.path.exists(my_cnf_path):
    from ConfigParser import SafeConfigParser
    config = SafeConfigParser()
    with open(my_cnf_path) as my_cnf:
        config.readfp(my_cnf)
        try:
            DATABASES['default']['PASSWORD'] = config.get('client', 'password')
        except ConfigParser.NoOptionError:
            pass