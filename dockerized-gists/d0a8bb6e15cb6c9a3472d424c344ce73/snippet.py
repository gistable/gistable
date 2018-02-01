import websocket
import ssl
import json
import threading
from time import sleep

ws = None
response = None

header = {'X-Qlik-User: UserDirectory=QLIKLOCAL; UserId=administrator'}

class ConnectQlikEngine:
    """
    Instantiates the Qlik Engine Service API
    """
    def __init__(self, server, certificate = False, clientkey = False, root = False):
        self.server = server
        self.certificate = certificate
        self.clientkey = clientkey
        self.root = root
        self.cur_id = 0
        thread = threading.Thread(target=self.ws_run)
        thread.start()
        sleep(1)     
    
    def next_id(self):
        """
        Incrementing ID for Json requests
        :return: The current ID
        """
        with threading.Lock():
            result = self.cur_id
            self.cur_id += 1
        return result 

# Main run, store the WS in global Variable ws
    def ws_run(self):
        global ws
        ws = websocket.WebSocketApp(self.server, 
                    on_message = self.on_message, 
                    on_error = self.on_error, 
                    header = header)
        ws.on_open = self.on_open

        certs = ({"ca_certs": self.root,
                       "certfile": self.certificate,
                       "keyfile": self.clientkey,
                       "cert_reqs": ssl.CERT_REQUIRED,
                       "server_side": False})
        ws.run_forever(sslopt = certs)
   
    def on_open(self, ws):
        self.next_id()

# Take the response of WS call and dump it in Global Variable Response, increment the currentID by 1
    def on_message(self, ws, message):
        global response
        response = json.loads(message)
        self.next_id()

    def on_error(self, ws, error):
        print(error)

# Qlik Sense Engine API Calls
    def open_doc(self, appid):
        request = {
            'method': 'OpenDoc',
            'params': [appid],
            'handle': -1,
            'id': self.cur_id, 
            'jsonrpc': '2.0'
            }
        json_request = json.dumps(request)
        ws.send(json_request)
        sleep(1)
        return response

    def get_activedoc(self):
        request = {
            'method': 'GetActiveDoc',
            'params': [],
            'handle': -1,
            'id': self.cur_id, 
            'jsonrpc': '2.0'
            }
        json_request = json.dumps(request)
        ws.send(json_request)
        sleep(1)
        return response

    def get_allinfos(self, qhandle):
        request = {
            'method': 'GetAllInfos',
            'params': [],
            'handle': qhandle,
            'id': self.cur_id, 
            'jsonrpc': '2.0'
            }
        json_request = json.dumps(request)
        ws.send(json_request)
        sleep(1)
        return response

    def get_script(self, qhandle):
        request = {
            'method': 'GetScript',
            'params': [],
            'handle': qhandle,
            'id': self.cur_id, 
            'jsonrpc': '2.0'
            }
        json_request = json.dumps(request)
        ws.send(json_request)
        sleep(1)
        return response

    def create_app(self, appname):
        request = {
            'method': 'CreateApp',
            'params': [appname],
            'handle': -1,
            'id': self.cur_id, 
            'jsonrpc': '2.0'
            }
        json_request = json.dumps(request)
        ws.send(json_request)
        sleep(1)
        return response

    def get_listoffieldshandle(self, qhandle):
        '''
        Do not call this function directly.  Used to source the handle of the Fields
        :param qhandle: handle of open document
        :return: qHandle of Object Field list
        '''
        request = {
            'method': 'CreateSessionObject',
            'params': [{ "qInfo": { "qId": "", "qType": "FieldList" }, 
                        "qFieldListDef": { "qShowSystem": True, "qShowHidden": True, "qShowSemantic": True, "qShowSrcTables": True } } ],
            'handle': qhandle,
            'id': self.cur_id, 
            'jsonrpc': '2.0'
            }
        json_request = json.dumps(request)
        ws.send(json_request)
        sleep(1)
        return response['result']['qReturn']['qHandle']

    def get_listoffields(self):
        request = {
            'method': 'GetLayout',
            'params': [],
            'handle': self.get_listoffieldshandle(qhandle),
            'id': self.cur_id, 
            'jsonrpc': '2.0'
            }
        json_request = json.dumps(request)
        ws.send(json_request)
        sleep(1)
        return response

if __name__ == "__main__":
    qes = ConnectQlikEngine(server='wss://qs2.qliklocal.net:4747', 
                    certificate='C:/certs/qs2.qliklocal.net/client.pem',
                    clientkey ='C:/certs/qs2.qliklocal.net/client_key.pem',
                    root='C:/certs/qs2.qliklocal.net/root.pem')

    qes.open_doc('d217c1d4-9d3b-4b90-8125-38df527a74bb')
    a = qes.get_activedoc()

    print (a)
    qhandle = a['result']['qReturn']['qHandle']

    print (qes.get_allinfos(qhandle))

    