import json
from os.path import exists
from requests import post, get
# Started today. 25 May.
# Updated 3 Oct.
class Callable:
    def __init__(self, method_name, token, safe=False):
        self.name = method_name
        self.token = token
        self.safe = safe
    def __call__(self, **kwargs):
        url = 'https://api.telegram.org/bot{}/{}'.format(self.token, self.name)
        json_res = post(url, data=kwargs).text
        if(not self.safe):
            try:
                json.loads(json_res)
            except:
                raise NotImplementedError('The method %s doesn\'t exists!' % self.name)
        res = json2obj(json_res)
        if(res.ok):
            return res.result
        else:
            raise Exception('Error code[{}]:\n{}'.format(res.error_code, res.description))

class minibot:
    def __init__(self, token):
        self.token = token
        self.safe = exists('functions.json')
        if(self.safe):
            with open('functions.json') as f:
                self.__dict__.update({x:Callable(x, token, True) for x in json.load(f)})
        else:
            print('functions file not found, running in unsafe mode.\nrun this script to fetch current methods.')

    def __getattr__(self, attr):
        return Callable(attr, self.token)

class json2obj(object):
    def __init__(self, string):
        self.json = json.loads(string)
        if('from' in self.json):
            self.json['from_user'] = self.json.pop('from')
        for x in self.json:
            if(self.json.__class__ == list):
                if(x.__class__.__name__ in ['list', 'dict']):
                    i = self.json.index(x)
                    self.json[i] = json2obj(json.dumps(self.json[i]))
            if(self.json.__class__ == dict):
                if(self.json[x].__class__.__name__ in ['list', 'dict']):
                    self.json[x] = json2obj(json.dumps(self.json[x]))
        if(self.json.__class__ != list):
            self.__dict__.update(self.json)

    def __getattr__(self, attr):
        inner_objects = list(filter(lambda x: isinstance(x, json2obj), self.__dict__.values()))
        if(len(inner_objects) > 0):
            for x in inner_objects:
                if(getattr(x, attr)):
                    return getattr(x, attr)
        return CustomFalse()


class CustomFalse(object):
    def __getattr__(self, attr):
        return CustomFalse()
    def __bool__(self):
        return False
    def __eq__(self, value):
        return False is value
    def __call__(self, *args, **kwargs):
        return False

if __name__ == '__main__':
    try:
        from lxml.html import fromstring
    except ImportError:
        print('lxml module is not installed, install it with\nsudo pip install lxml\nor\nsudo easy_install lxml' )
        sys.exit(1)
    xpath_list = fromstring(get('https://core.telegram.org/bots/api').text).xpath('//*/h4/text()')
    current_methods = list(filter(lambda i: i[0].islower(), xpath_list))
    json.dump(current_methods, open('functions.json', 'w'), indent=1)