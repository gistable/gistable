import platform
import requests


class SeedBox:
    def __init__(self, agentConfig, checksLogger, rawConfig):
        self.agentConfig = agentConfig
        self.checksLogger = checksLogger
        self.rawConfig = rawConfig
        self.version = platform.python_version_tuple()

        self.uuid = '8888888-bd96-11e3-8ed6-174023235e0f'
        self.token = '7k1sv2t9lv30yrzgk8dxi529'

        self.fields = ['light', 'temperature', 'humidity']

    def run(self):

        data = {}
        for field in self.fields:
            data[field] = 0

        try:
            r = requests.get('http://localhost:3000/data/%s?token=%s' % (self.uuid, self.token,))

            for field in self.fields:
                data[field] = r.json()['data'][0][field]
        except:
            pass
        return data