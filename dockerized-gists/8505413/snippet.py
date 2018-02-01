config_dict = {
    'group1': {
        'server1': {
            'apps': ('nginx', 'mysql'),
            'cpus': 4
        },
        'maintenance': True
    },
    'firewall_version': '1.2.3',
    'python2.7': True
}

class DictToObject(object):

    def __init__(self, dictionary):
        def _traverse(key, element):
            if isinstance(element, dict):
                return key, DictToObject(element)
            else:
                return key, element
                
        object_dict = dict(_traverse(k, v) for k, v in dictionary.iteritems())
        self.__dict__.update(object_dict)
        
if __name__ == '__main__':
    config = DictToObject(config_dict)
    assert config.group1.server1.apps == ('nginx', 'mysql')
    assert config.group1.maintenance
    assert config.firewall_version == '1.2.3'
    assert config.__dict__['python2.7'] # or
    assert config.__getattribute__('python2.7')
