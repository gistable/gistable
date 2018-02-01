import json
import requests


class Action(object):

    def __init__(self, entity, name):
        self.civi = entity.civi
        self.entity_name = entity.name
        self.name = name

    def __repr__(self):
        return '<Action %s.%s.%s>' % (
            repr(self.civi), self.entity_name, self.name)

    def __call__(self, **kw):
        url = self.civi.endpoint
        if self.entity_name in ('CustomGroup', 'CustomField', 'OptionGroup', 'OptionValue', 'GroupContact'):
            entity = self.entity_name
        else:
            entity = self.entity_name.lower()
        params = {
            'json': '1',
            'version': '3',
            'api_key': self.civi.user_key,
            'key': self.civi.site_key,
            'action': self.name,
            'entity': entity,
        }
        if self.civi.debug:
            params['debug'] = '1'
        if kw:
            params['json'] = json.dumps(kw)
        res = requests.post(url, params=params).json()
        if res['is_error']:
            raise Exception(res['error_message'])
        if res['values'] == False:
            return []
        if isinstance(res['values'], list):
            return res['values']
        if isinstance(res['values'], int):
            return res['values']
        return res['values'].values()


class Entity(object):

    def __init__(self, civi, name):
        self.civi = civi
        self.name = name

    def __getattr__(self, name):
        # XXX validate
        return Action(self, name)

    def __repr__(self):
        return '<Entity %s.%s>' % (self.civi, self.name)


class CiviCRM(object):

    def __init__(self, endpoint, site_key, user_key, debug=False):
        self.endpoint = endpoint + '/sites/all/modules/civicrm/extern/rest.php'
        self.site_key = site_key
        self.user_key = user_key
        self.debug = debug

    def __getattr__(self, name):
        # XXX validate
        return Entity(self, name)

    def __repr__(self):
        return 'CiviCRM(%s)' % repr(self.endpoint)


# example:
# civi = CiviCRM('path/to/civicrm', SITE_KEY, USER_KEY)
# tags = civi.Tag.get(rowCount=10000)
