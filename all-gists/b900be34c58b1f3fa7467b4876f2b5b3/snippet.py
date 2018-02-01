import requests
import json
import random
import string
import sys

class ApiRequest:

    def __init__(self, uid, secret, key="", url="http://localhost:5000/login"):
        self.secret = secret
        self.uid = uid
        self.key = key
        self.url = url
        if self.key == "":
            try:
                with open(".refresh_token") as f:
                    self.key = f.read().strip()
            except:
                self.key = self.new_token().json()['access_token']


    def get(self, uri, methods="GET"):
        h = {'Authorization': 'Bearer ' + self.key}
        r = requests.request(methods, "https://api.intra.42.fr" + uri, headers=h, allow_redirects=False)
        try:
            if r.json()['error'] == "Not authorized":
                print("Key expired !!!")
                print(self.key)
                self.key = self.new_token().json()['access_token']
                print(self.key)
                print("Key DONE !!!")
                return self.get(uri, methods)
        except:
            pass
        return r

    def get_user(self, uri, key, methods="GET"):
        h = {'Authorization': 'Bearer ' + key}
        r = requests.request(methods, "https://api.intra.42.fr" + uri, headers=h, allow_redirects=False)
        return r

    def new_token(self):
        d = {'grant_type': 'client_credentials', 'client_id': self.uid, 'client_secret': self.secret}
        r = requests.post("https://api.intra.42.fr/oauth/token", data=d)
        print (r.json())
        with open(".refresh_token", "w") as f:
            f.write(r.json()['access_token'])
        return r

    def connect_page(self):
        state = ''.join(random.choice(string.ascii_letters) for i in range(64))
        return ("https://api.intra.42.fr/oauth/authorize?client_id=" + self.uid
                + "&redirect_uri=" + self.url + "&scope=public&state=" + state + "&response_type=code")

    def connect_user(self, code, state):
        d = {'grant_type': 'authorization_code', 'client_id': self.uid, 'client_secret': self.secret,
        'code': code, 'redirect_uri':self.url}
        r = requests.post("https://api.intra.42.fr/oauth/token", data=d)
        print(r.text)
        return r

uid=""
secret=""
key=""

api = ApiRequest(uid, secret, key)
if __name__ == '__main__':
    raw = False
    save = False
    if len(sys.argv) > 1 and sys.argv[1] == "-r":
        raw = True
    if len(sys.argv) > 1 and sys.argv[1] == "-s":
        save = True

    while True:
        try:
            p = input("Page ?> ").strip()
            if p == "exit":
                break
            if p == "":
                continue
            r = api.get(p)
            print (r.headers)
            if raw:
                print (r.json())
            elif save:
                with open('ttt', 'w') as fi:
                    fi.write(json.dumps(r.json(), separators=(',',':')))
            else:
                print (json.dumps(r.json(), indent=4, separators=(',', ': ')))
        except:
            print ("ERROR")