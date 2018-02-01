import requests

ENDPOINT = 'https://www.softaculous.com/noc'

SERVERTYPE_DEDICATED = 1
SERVERTYPE_VPS = 2


class Client(object):
    def __init__(self, username, password):
        self._args = {'nocname': username, 'nocpass': password, 'json': 1}

    def __call__(self, **kwargs):
        kwargs.update(self._args)
        response = requests.get(ENDPOINT, params=kwargs)
        response.raise_for_status()
        parsed = response.json()
        print parsed
        if 'error' in parsed and parsed['error']:
            raise SoftaculousError(parsed)
        return parsed

    def buy(self, ip, email, autorenew=True, term='1M', servertype=SERVERTYPE_VPS):
        response = self(ca='softaculous_buy', purchase=1, ips=ip, toadd=term,
                          servertype=servertype, authemail=email,
                          autorenew=autorenew)

    def cancel(self, key=None, ip=None):
        if not any((key, ip)):
            raise ValueError('Please specify a value for either key or ip')
        return self(ca='softaculous_cancel', lickey=key, licip=ip,
                          cancel_license=1)

    def licenses(self, ip=None, email=None, key=None, expiry=None, limit=50, offset=0):
        response = self(ca='softaculous', ips=ip, email=email,
                          lickey=key, len=limit, start=offset, expiry=expiry)
        if not response['licenses']:
            return ()
        return tuple(License(self, **license) for _, license in response['licenses'].items())

    def licenselogs(self, key, limit=None):
        response = self(ca='softaculous_licenselogs', key=key, limit=limit)
        actions = tuple((Action(self, **action) for _, action in response['actions'].items()))
        license = License(self, **response['license'])
        return license, actions

    def refund(self, actid):
        return self(ca='softaculous_refund', actid=actid)


class SoftaculousError(Exception):
    def __init__(self, response):
        super(SoftaculousError, self).__init__(response['error'].items()[0])


class SoftaculousObject(object):
    _idname = ''

    def __init__(self, client, **properties):
        self._client = client
        self._properties = properties

    def __getattr__(self, attr):
        if attr not in self._properties:
            raise AttributeError("%r object has no attribute %r" %
                         (self.__class__, attr))
        return self._properties[attr]

    def __str__(self):
        return self._properties[self._idname]

    def __repr__(self):
        return '<{}({})>'.format(type(self).__name__, str(self))


class License(SoftaculousObject):
    _idname = 'lid'

    def cancel(self):
        return self._client.cancel(self.license)

    def logs(self, limit=None):
        license, action = self._client.licenselogs(self.license, limit)
        self._properties = license
        return action


class Action(SoftaculousObject):
    _idname = 'actid'

    def refund(self):
        self._client.refund(self.actid)
